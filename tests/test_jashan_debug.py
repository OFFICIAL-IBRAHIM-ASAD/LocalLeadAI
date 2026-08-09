from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator
from app.scraper.scroller import GoogleMapsScroller

browser_manager = BrowserManager()
page = browser_manager.start()

navigator = GoogleMapsNavigator(page)
navigator.search("Restaurants in Karachi")

scroller = GoogleMapsScroller(page)
scroller.scroll()

result_links = page.locator('a[href*="/place/"]')

# Jashan was BUSINESS 2 in your output -> index 1
link = result_links.nth(1)

print("--- LINK TEXT ---")
print(link.inner_text())

card = link.locator('xpath=ancestor::div[@role="article"]').first
print("\n--- CARD HTML ---")
print(card.inner_html())

input("Press ENTER to close...")
browser_manager.close()