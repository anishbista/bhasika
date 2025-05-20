import requests

API_URL = "https://testnpapi.hobes.tech/testnp/blogs/get-blog-pageable"
row = 10
page = 1

while True:
    payload = {"row": row, "page": page}
    response = requests.post(API_URL, json=payload)
    if response.status_code != 200:
        print(f"Failed to fetch blogs: {response.status_code}")
        break

    blogs = response.json()
    content = blogs.get("data", {}).get("content", [])
    if not content:
        break

    for blog in content:
        print(page, blog)

    total_pages = blogs.get("data", {}).get("totalPages", 1)
    if page >= total_pages:
        break
    page += 1
