// 添加书籍
async function addBook() {
    const title = document.getElementById('title').value;
    const author = document.getElementById('author').value;
    const isbn = document.getElementById('isbn').value;

    const response = await fetch('/add_book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, author, isbn }),
    });
    const result = await response.json();
    alert(result.message);
}

// 查找书籍
async function findBook() {
    const title = document.getElementById('searchTitle').value;
    const response = await fetch(`/find_book/${title}`);
    const result = await response.json();
    const searchResult = document.getElementById('searchResult');
    if (response.status === 200) {
        searchResult.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    } else {
        searchResult.innerHTML = result.message;
    }
}

// 显示所有书籍
async function showAllBooks() {
    const response = await fetch('/books');
    const result = await response.json();
    const bookList = document.getElementById('bookList');
    if (response.status === 200) {
        bookList.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    } else {
        bookList.innerHTML = result.message;
    }
}