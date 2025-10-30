#!/usr/bin/env python3
"""Финальный тест - парсинг с сохранением в JSON"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from deepscraper.runner.browser import BrowserRunner

async def final_parsing_test():
    """Финальный тест с сохранением данных"""
    print("🚀 ФИНАЛЬНЫЙ ТЕСТ: Парсинг с сохранением результатов...")

    runner = BrowserRunner()
    results = []

    try:
        async with runner.context() as page:
            await runner.navigate(page, "https://books.toscrape.com")
            await page.wait_for_load_state("networkidle")

            print("📊 Собираем данные о книгах...")

            # Извлекаем все данные о книгах
            books_data = await page.evaluate("""
                () => {
                    const books = [];
                    const articles = document.querySelectorAll('article.product_pod');

                    articles.forEach(article => {
                        const title = article.querySelector('h3 a')?.title || article.querySelector('h3 a')?.textContent.trim();
                        const price = article.querySelector('.price_color')?.textContent.trim();
                        const availability = article.querySelector('.instock.availability')?.textContent.trim().replace(/\s+/g, ' ');
                        const link = article.querySelector('h3 a')?.href;

                        if (title && price) {
                            books.push({
                                title: title,
                                price: price,
                                availability: availability || 'In stock',
                                link: link ? new URL(link, window.location.href).href : ''
                            });
                        }
                    });

                    return books;
                }
            """)

            # Сохраняем результаты
            results = books_data[:10]  # Берем первые 10 книг

            print(f"✅ Собрано {len(results)} книг:")
            for i, book in enumerate(results):
                print(f"   {i+1}. {book['title']} - {book['price']}")

            # Сохраняем в JSON
            output_data = {
                "source": "https://books.toscrape.com",
                "scraped_at": datetime.now().isoformat(),
                "books_count": len(results),
                "books": results
            }

            with open("parsing_results.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print("💾 Результаты сохранены в parsing_results.json")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("🎉 ФИНАЛЬНЫЙ ТЕСТ ЗАВЕРШЕН!")
    return results

if __name__ == "__main__":
    books = asyncio.run(final_parsing_test())
    print(f"\n📈 ИТОГ: Успешно собрано {len(books)} книг")