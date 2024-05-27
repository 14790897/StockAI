from financial_utils import (
    get_stock_data,
    get_sentiment_analysis,
    get_industry_analysis,
    get_final_analysis,
    get_current_price,
    generate_ticker_ideas,
    rank_companies,
    get_analyst_ratings,
)

# User input
industry = input("Enter the industry to analyze: ")
years = 1  # int(input("Enter the number of years for analysis: "))

# Generate ticker ideas for the industry
tickers = generate_ticker_ideas(industry)
print(f"\nTicker Ideas for {industry} Industry:")
print(", ".join(tickers))

# Perform analysis for each company
analyses = {}
prices = {}
for ticker in tickers:
    try:
        print(f"\nAnalyzing {ticker}...")
        hist_data, balance_sheet, financials, news = get_stock_data(ticker, years)
        main_data = {
            "hist_data": hist_data,
            "balance_sheet": balance_sheet,
            "financials": financials,
            "news": news,
        }
        sentiment_analysis = get_sentiment_analysis(ticker, news)
        analyst_ratings = get_analyst_ratings(ticker)
        industry_analysis = get_industry_analysis(ticker)
        final_analysis = get_final_analysis(
            ticker, {}, sentiment_analysis, analyst_ratings, industry_analysis
        )
        analyses[ticker] = final_analysis
        prices[ticker] = get_current_price(ticker)
    except:
        pass

# Rank the companies based on their analyses
ranking = rank_companies(industry, analyses, prices)
print(f"\nRanking of Companies in the {industry} Industry:")
print(ranking)
