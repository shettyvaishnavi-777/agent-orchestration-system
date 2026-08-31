from ddgs import DDGS


def web_search(query: str, max_results: int = 5):

    results = []

    with DDGS() as ddgs:

        search_results = ddgs.text(
            query,
            max_results=max_results
        )

        for result in search_results:

            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })

    return results


# Test tool
if __name__ == "__main__":

    results = web_search("electric vehicles benefits")

    print("\n====================================")
    print("          WEB SEARCH TOOL")
    print("====================================")

    for result in results:

        print("\nTitle:", result["title"])
        print("URL:", result["url"])
        print("Description:", result["snippet"])

    print("\n====================================")
    print("       SEARCH COMPLETED")
    print("====================================")