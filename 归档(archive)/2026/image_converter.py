#!/usr/bin/env python3
"""
通用图片批量转码工具 - ImageBatchConverter
支持多种格式转换，智能错误处理，批量处理功能
"""

import os
import sys
import argparse
import concurrent.futures
from pathlib import Path
from datetime import datetime
import json
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, asdict
import hashlib

# 尝试导入必要的库
try:
    from PIL import Image, ImageOps, UnidentifiedImageError
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("警告: Pillow库未安装，部分功能可能受限")

# 可选功能支持
SUPPORTED_PLUGINS = {
    'avif': False,
    'heic': False,
    'webp': True  # PIL原生支持
}

# 检查插件支持
if HAS_PILLOW:
    try:
        import pillow_avif
        SUPPORTED_PLUGINS['avif'] = True
    except ImportError:
        pass
    
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        SUPPORTED_PLUGINS['heic'] = True
    except ImportError:
        pass

@dataclass
class ConversionResult:
    """转换结果记录"""
    input_file: str
    output_file: str
    success: bool
    error_message: str = ""
    original_size: int = 0
    converted_size: int = 0
    conversion_time: float = 0.0
    original_format: str = ""
    converted_format: str = ""

class ImageBatchConverter:
    """图片批量转换器"""
    
    # 支持转换的格式映射
    FORMAT_MAPPING = {
        'jpg': 'JPEG',
        'jpeg': 'JPEG',
        'png': 'PNG',
        'webp': 'WEBP',
        'bmp': 'BMP',
        'gif': 'GIF',
        'tiff': 'TIFF',
        'tif': 'TIFF',
        'avif': 'AVIF' if SUPPORTED_PLUGINS['avif'] else None,
        'heic': 'HEIF' if SUPPORTED_PLUGINS['heic'] else None,
    }
    
    # 支持的输入格式
    INPUT_FORMATS = [
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', 
        '.tiff', '.tif', '.webp', '.jfif', '.jp2'
    ]
    
    # 添加插件支持的格式
    if SUPPORTED_PLUGINS['avif']:
        INPUT_FORMATS.extend(['.avif', '.avifs'])
    if SUPPORTED_PLUGINS['heic']:
        INPUT_FORMATS.extend(['.heic', '.heif'])
    
    def __init__(self, config: Dict):
        self.config = config
        self.results: List[ConversionResult] = []
        self.total_files = 0
        self.processed_files = 0
        
        # 验证配置
        self._validate_config()
        
        # 创建输出目录
        self.output_dir = Path(config['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建备份目录（如果需要）
        if config.get('backup_before_convert'):
            self.backup_dir = self.output_dir / 'backup'
            self.backup_dir.mkdir(exist_ok=True)
    
    def _validate_config(self):
        """验证配置参数"""
        if not HAS_PILLOW:
            raise ImportError("Pillow库未安装，请运行: pip install Pillow")
        
        # 检查输出格式支持
        output_format = self.config['output_format'].lower()
        if output_format not in self.FORMAT_MAPPING:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        if self.FORMAT_MAPPING[output_format] is None:
            plugin = 'avif' if output_format == 'avif' else 'heic'
            raise ImportError(f"{output_format.upper()}格式需要安装插件: pip install pillow-{plugin}-plugin")
        
        # 检查质量参数
        if self.config['quality'] < 1 or self.config['quality'] > 100:
            raise ValueError("质量参数必须在1-100之间")
        
        # 检查尺寸参数
        if (self.config.get('max_width') or self.config.get('max_height')) and \
           (self.config.get('resize_width') or self.config.get('resize_height')):
            raise ValueError("不能同时设置最大尺寸和固定尺寸")
    
    def _should_process_file(self, file_path: Path) -> bool:
        """判断是否应该处理该文件"""
        # 检查扩展名
        if file_path.suffix.lower() not in self.INPUT_FORMATS:
            return False
        
        # 检查文件大小
        file_size = file_path.stat().st_size
        if self.config.get('min_file_size') and file_size < self.config['min_file_size']:
            return False
        if self.config.get('max_file_size') and file_size > self.config['max_file_size']:
            return False
        
        # 检查文件名模式
        if self.config.get('filename_pattern'):
            import fnmatch
            if not fnmatch.fnmatch(file_path.name, self.config['filename_pattern']):
                return False
        
        return True
    
    def _collect_files(self, input_path: Path) -> List[Path]:
        """收集要处理的文件"""
        files = []
        
        if input_path.is_file():
            # 单个文件
            if self._should_process_file(input_path):
                files.append(input_path)
        else:
            # 目录
            for pattern in self.config.get('patterns', ['*']):
                for file_path in input_path.rglob(pattern) if self.config.get('recursive') else input_path.glob(pattern):
                    if file_path.is_file() and self._should_process_file(file_path):
                        files.append(file_path)
        
        return files
    
    def _create_output_path(self, input_file: Path) -> Path:
        """创建输出路径"""
        # 保持目录结构
        if self.config.get('preserve_structure') and not self.config['input_path'].is_file():
            relative_path = input_file.relative_to(self.config['input_path'])
            output_path = self.output_dir / relative_path
        else:
            output_path = self.output_dir / input_file.name
        
        # 修改扩展名
        output_path = output_path.with_suffix(f'.{self.config["output_format"]}')
        
        # 处理文件名冲突
        if not self.config.get('overwrite'):
            counter = 1
            original_output_path = output_path
            while output_path.exists():
                output_path = original_output_path.with_stem(
                    f"{original_output_path.stem}_{counter}"
                )
                counter += 1
        
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return output_path
    
    def _backup_file(self, file_path: Path):
        """备份文件"""
        if self.config.get('backup_before_convert'):
            backup_path = self.backup_dir / file_path.relative_to(self.config['input_path'])
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(file_path, backup_path)
    
    def _process_single_image(self, input_file: Path) -> ConversionResult:
        """处理单个图片文件"""
        import time
        
        start_time = time.time()
        output_file = self._create_output_path(input_file)
        result = ConversionResult(
            input_file=str(input_file),
            output_file=str(output_file),
            success=False,
            original_format=input_file.suffix.lower()[1:],
            converted_format=self.config['output_format']
        )
        
        try:
            # 记录原始大小
            result.original_size = input_file.stat().st_size
            
            # 备份文件
            if self.config.get('backup_before_convert'):
                self._backup_file(input_file)
            
            # 打开图片
            with Image.open(input_file) as img:
                # 验证图片
                img.verify()
            
            # 重新打开（因为verify会关闭文件）
            with Image.open(input_file) as img:
                # 处理EXIF方向
                if self.config.get('autorotate'):
                    img = ImageOps.exif_transpose(img)
                
                # 转换为RGB/RGBA模式
                target_mode = 'RGBA' if self.config['output_format'].lower() in ['png', 'webp'] and img.mode in ('RGBA', 'LA') else 'RGB'
                
                if img.mode != target_mode:
                    if img.mode == 'P':
                        img = img.convert('RGBA' if 'A' in target_mode else 'RGB')
                    elif img.mode in ('RGBA', 'LA') and target_mode == 'RGB':
                        # 透明背景处理
                        if self.config.get('transparent_background'):
                            # 保持透明通道
                            target_mode = 'RGBA'
                        else:
                            # 填充白色背景
                            rgb_img = Image.new('RGB', img.size, self.config.get('background_color', (255, 255, 255)))
                            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = rgb_img
                    else:
                        img = img.convert(target_mode)
                
                # 调整尺寸
                if self.config.get('resize_width') or self.config.get('resize_height'):
                    new_size = (
                        self.config.get('resize_width') or img.width,
                        self.config.get('resize_height') or img.height
                    )
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                elif self.config.get('max_width') or self.config.get('max_height'):
                    max_width = self.config.get('max_width', img.width)
                    max_height = self.config.get('max_height', img.height)
                    
                    # 计算等比例缩放
                    width_ratio = max_width / img.width
                    height_ratio = max_height / img.height
                    ratio = min(width_ratio, height_ratio)
                    
                    if ratio < 1:
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存选项
                save_kwargs = {
                    'quality': self.config['quality'],
                    'optimize': self.config.get('optimize', True),
                }
                
                # 格式特定的选项
                format_upper = self.FORMAT_MAPPING[self.config['output_format'].lower()]
                if format_upper == 'JPEG':
                    save_kwargs['progressive'] = self.config.get('progressive', True)
                elif format_upper == 'PNG':
                    save_kwargs['compress_level'] = self.config.get('compress_level', 6)
                elif format_upper == 'WEBP':
                    save_kwargs['method'] = self.config.get('webp_method', 4)
                
                # 保存图片
                img.save(output_file, format_upper, **save_kwargs)
                
                # 记录结果
                result.converted_size = output_file.stat().st_size
                result.success = True
                
        except UnidentifiedImageError:
            result.error_message = "无法识别的图片格式"
        except Exception as e:
            result.error_message = str(e)
        
        result.conversion_time = time.time() - start_time
        return result
    
    def convert(self) -> Dict:
        """执行批量转换"""
        input_path = Path(self.config['input_path'])
        
        if not input_path.exists():
            return {"error": f"输入路径不存在: {input_path}"}
        
        # 收集文件
        files = self._collect_files(input_path)
        self.total_files = len(files)
        
        if self.total_files == 0:
            return {"error": "没有找到符合条件的图片文件"}
        
        print(f"找到 {self.total_files} 个文件需要处理")
        
        # 使用线程池并行处理
        max_workers = min(self.config.get('max_workers', 4), self.total_files)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_file = {
                executor.submit(self._process_single_image, file): file 
                for file in files
            }
            
            # 处理结果
            for future in concurrent.futures.as_completed(future_to_file):
                self.processed_files += 1
                result = future.result()
                self.results.append(result)
                
                # 打印进度
                if result.success:
                    compression = (1 - result.converted_size / result.original_size) * 100 if result.original_size > 0 else 0
                    print(f"[{self.processed_files}/{self.total_files}] ✓ {Path(result.input_file).name} -> {Path(result.output_file).name} "
                          f"({result.original_size/1024:.1f}KB → {result.converted_size/1024:.1f}KB, 压缩: {compression:.1f}%)")
                else:
                    print(f"[{self.processed_files}/{self.total_files}] ✗ {Path(result.input_file).name}: {result.error_message}")
        
        # 生成统计信息
        stats = self._generate_statistics()
        
        # 保存转换日志
        if self.config.get('save_log'):
            self._save_conversion_log(stats)
        
        return stats
    
    def _generate_statistics(self) -> Dict:
        """生成统计信息"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        total_original_size = sum(r.original_size for r in successful)
        total_converted_size = sum(r.converted_size for r in successful)
        total_time = sum(r.conversion_time for r in self.results)
        
        stats = {
            "total_files": self.total_files,
            "successful": len(successful),
            "failed": len(failed),
            "total_original_size": total_original_size,
            "total_converted_size": total_converted_size,
            "total_time": total_time,
            "average_time": total_time / self.total_files if self.total_files > 0 else 0,
            "compression_ratio": (1 - total_converted_size / total_original_size) * 100 if total_original_size > 0 else 0,
            "failed_files": [asdict(r) for r in failed]
        }
        
        return stats
    
    def _save_conversion_log(self, stats: Dict):
        """保存转换日志"""
        log_file = self.output_dir / f"conversion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "statistics": stats,
            "results": [asdict(r) for r in self.results]
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"转换日志已保存: {log_file}")

def main():
    parser = argparse.ArgumentParser(
        description='通用图片批量转码工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法: 转换为JPG格式
  python image_converter.py ./images -o ./output -f jpg
  
  # 转换为PNG格式，保持透明通道
  python image_converter.py ./images -o ./output -f png --transparent-background
  
  # 转换为WebP，设置质量并调整尺寸
  python image_converter.py ./images -o ./output -f webp -q 80 --max-width 1920
  
  # 递归处理子目录，保持目录结构
  python image_converter.py ./images -o ./output -f jpg -r --preserve-structure
  
  # 批量重设尺寸
  python image_converter.py ./images -o ./output --resize-width 800 --resize-height 600
  
  # 并行处理，备份原文件
  python image_converter.py ./images -o ./output -f jpg --max-workers 8 --backup

支持的输入格式: JPG, PNG, BMP, GIF, TIFF, WebP, AVIF*, HEIC*
*需要安装相应插件
        """
    )
    
    # 必需参数
    parser.add_argument('input_path', help='输入文件或目录路径')
    parser.add_argument('-o', '--output-dir', required=True, help='输出目录路径')
    parser.add_argument('-f', '--format', required=True, choices=['jpg', 'jpeg', 'png', 'webp', 'bmp', 'gif', 'tiff'],
                       help='输出格式')
    
    # 质量与优化
    parser.add_argument('-q', '--quality', type=int, default=85,
                       help='输出质量 (1-100，默认: 85)')
    parser.add_argument('--no-optimize', action='store_false', dest='optimize',
                       help='禁用图片优化')
    parser.add_argument('--progressive', action='store_true',
                       help='生成渐进式JPEG图片')
    
    # 尺寸调整
    size_group = parser.add_argument_group('尺寸调整')
    size_group.add_argument('--resize-width', type=int, help='固定宽度（像素）')
    size_group.add_argument('--resize-height', type=int, help='固定高度（像素）')
    size_group.add_argument('--max-width', type=int, help='最大宽度（像素）')
    size_group.add_argument('--max-height', type=int, help='最大高度（像素）')
    
    # 颜色与背景
    color_group = parser.add_argument_group('颜色与背景')
    color_group.add_argument('--transparent-background', action='store_true',
                           help='保持透明背景（仅PNG/WebP）')
    color_group.add_argument('--background-color', type=str, default='#FFFFFF',
                           help='背景颜色（十六进制，默认: #FFFFFF）')
    color_group.add_argument('--autorotate', action='store_true',
                           help='根据EXIF信息自动旋转图片')
    
    # 文件处理
    file_group = parser.add_argument_group('文件处理')
    file_group.add_argument('-r', '--recursive', action='store_true',
                          help='递归处理子目录')
    file_group.add_argument('--preserve-structure', action='store_true',
                          help='保持原始目录结构')
    file_group.add_argument('--overwrite', action='store_true',
                          help='覆盖已存在的文件')
    file_group.add_argument('--backup', action='store_true',
                          help='转换前备份原文件')
    file_group.add_argument('--pattern', default='*', help='文件名匹配模式')
    file_group.add_argument('--min-size', type=int, help='最小文件大小（字节）')
    file_group.add_argument('--max-size', type=int, help='最大文件大小（字节）')
    
    # 性能与日志
    perf_group = parser.add_argument_group('性能与日志')
    perf_group.add_argument('--max-workers', type=int, default=4,
                          help='最大并行工作数（默认: 4）')
    perf_group.add_argument('--save-log', action='store_true',
                          help='保存转换日志')
    perf_group.add_argument('--verbose', action='store_true',
                          help='显示详细信息')
    
    args = parser.parse_args()
    
    # 构建配置字典
    config = {
        'input_path': args.input_path,
        'output_dir': args.output_dir,
        'output_format': args.format,
        'quality': args.quality,
        'optimize': args.optimize,
        'progressive': args.progressive,
        'recursive': args.recursive,
        'preserve_structure': args.preserve_structure,
        'overwrite': args.overwrite,
        'backup_before_convert': args.backup,
        'transparent_background': args.transparent_background,
        'autorotate': args.autorotate,
        'save_log': args.save_log,
        'max_workers': args.max_workers,
        'patterns': [args.pattern],
    }
    
    # 添加可选参数
    if args.resize_width or args.resize_height:
        config['resize_width'] = args.resize_width
        config['resize_height'] = args.resize_height
    
    if args.max_width or args.max_height:
        config['max_width'] = args.max_width
        config['max_height'] = args.max_height
    
    if args.background_color:
        # 转换十六进制颜色为RGB元组
        color = args.background_color.lstrip('#')
        if len(color) == 6:
            config['background_color'] = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    if args.min_size:
        config['min_file_size'] = args.min_size
    
    if args.max_size:
        config['max_file_size'] = args.max_size
    
    try:
        # 显示插件支持情况
        print("=" * 60)
        print("图片批量转码工具")
        print("=" * 60)
        
        if SUPPORTED_PLUGINS['avif']:
            print("✓ AVIF格式支持: 已启用")
        else:
            print("⚠ AVIF格式支持: 需要安装 pillow-avif-plugin")
        
        if SUPPORTED_PLUGINS['heic']:
            print("✓ HEIC格式支持: 已启用")
        else:
            print("⚠ HEIC格式支持: 需要安装 pillow-heif")
        
        print("-" * 60)
        
        # 创建转换器并执行
        converter = ImageBatchConverter(config)
        stats = converter.convert()
        
        # 显示统计信息
        print("\n" + "=" * 60)
        print("转换统计:")
        print(f"总文件数: {stats['total_files']}")
        print(f"成功: {stats['successful']}")
        print(f"失败: {stats['failed']}")
        print(f"原始总大小: {stats['total_original_size'] / 1024 / 1024:.2f} MB")
        print(f"转换后总大小: {stats['total_converted_size'] / 1024 / 1024:.2f} MB")
        print(f"压缩率: {stats['compression_ratio']:.1f}%")
        print(f"总耗时: {stats['total_time']:.2f}秒")
        print(f"平均每张: {stats['average_time']:.2f}秒")
        print("=" * 60)
        
        if stats['failed'] > 0:
            print(f"\n失败文件列表:")
            for failed in stats['failed_files'][:5]:  # 只显示前5个
                print(f"  - {Path(failed['input_file']).name}: {failed['error_message']}")
            if stats['failed'] > 5:
                print(f"  ... 还有 {stats['failed'] - 5} 个失败文件")
        
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if not HAS_PILLOW:
        print("错误: 需要安装Pillow库")
        print("请运行: pip install Pillow")
        print("可选插件:")
        print("  - AVIF支持: pip install pillow-avif-plugin")
        print("  - HEIC支持: pip install pillow-heif")
        sys.exit(1)
    
    main()