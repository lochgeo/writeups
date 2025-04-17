# Comprehensive Report on Vendor-Provided Foreign Exchange Systems

## Introduction
Foreign exchange (FX) systems are critical tools for businesses, traders, and financial institutions to manage currency trading, international payments, and exchange rate risks. These systems, often provided by specialized vendors, include software platforms, APIs, and data feeds that facilitate real-time pricing, order execution, and analytics. This report identifies key vendor-provided FX systems, examines whether they have published data models or documentation, and provides a table with links to their documentation, as requested. This updated version includes Bloomberg’s FXGO platform and clarifies the status of Nfino, which was queried but not found to be a player in the FX space.

## Methodology
To compile this report, I conducted a thorough analysis of available web resources, focusing on reputable sources such as industry reviews, vendor websites, and developer portals. The process involved:
- Identifying major vendors in the FX software market.
- Verifying the availability of published data models or documentation for their systems.
- Compiling a table with links to the documentation, where accessible.
The information is current as of April 17, 2025, and is based on publicly available data from trusted sources. Additional searches were conducted to confirm the inclusion of Bloomberg’s FXGO and to investigate Nfino’s potential role in the FX market.

## Key Vendor-Provided Systems
The FX software market includes a range of vendors offering platforms for trading, data access, and risk management. Based on the analysis, the following vendors are among the most prominent, with evidence of published documentation or data models:

### 1. Bloomberg
- **System**: FXGO
- **Description**: FXGO is Bloomberg’s premier multi-bank electronic trading platform, integrated with the Bloomberg Terminal. It connects price takers (e.g., asset managers, corporations) to over 800 liquidity providers across 140 countries, supporting trading in spot, outrights, swaps, non-deliverable forwards (NDFs), deposits, precious metals, and options for any currency pair and tenor. Features include real-time pricing, request-for-quote (RFQ) and streaming capabilities, netting, pre- and post-trade allocations, and straight-through processing (STP) for integration with order management, risk, and back-office systems.
- **Documentation and Data Models**: Bloomberg provides detailed API documentation for FXGO through its developer portal and Bloomberg Terminal resources. This includes specifications for pricing, trade execution, and analytics data models, such as those used in Pricing Quality Analytics (MISX) and the Supplementary Cost Analysis Tool. Access to full documentation may require a Bloomberg Terminal subscription or developer account.
- **Link**: [Bloomberg Developer Portal](https://www.bloomberg.com/professional/support/api-library/)

### 2. MetaQuotes
- **System**: MetaTrader platforms (MetaTrader 4 and MetaTrader 5)
- **Description**: MetaQuotes is a leading developer of trading platforms for financial markets, particularly in FX. MetaTrader 5 is a multi-asset platform that supports FX trading with advanced charting, automated trading, and real-time data.
- **Documentation and Data Models**: MetaQuotes provides extensive documentation for MetaTrader, including the MQL5 Reference for programming trading strategies and APIs. The documentation includes standard library classes that define data models for trading strategies, custom indicators, and file access. Books like "MQL5 Programming for Traders" are also available.
- **Link**: [MetaTrader Docs](https://www.mql5.com/en/docs)

### 3. Saxo Bank
- **System**: SaxoOpenAPI
- **Description**: Saxo Bank offers a REST-like API for building high-performance, multi-asset trading platforms. It supports FX trading with features like streaming quotes, order placement, and portfolio management.
- **Documentation and Data Models**: The SaxoOpenAPI developer portal provides detailed reference documentation, including endpoint descriptions and complex data types (e.g., AccountType). This documentation defines data models for FX-related resources, such as instrument details and market data.
- **Link**: [Saxo OpenAPI](https://www.developer.saxo/openapi/referencedocs)

### 4. Refinitiv (LSEG)
- **System**: Refinitiv Data Platform
- **Description**: Refinitiv, now part of the London Stock Exchange Group (LSEG), provides comprehensive FX data through its Data Platform. This includes real-time pricing, historical data, and benchmarks for over 150 currencies, accessible via APIs and data feeds.
- **Documentation and Data Models**: The LSEG developer portal offers an API catalog with documentation for accessing FX data. The Refinitiv Data Library for Python and other APIs provide consistent data models across access points (e.g., desktop, cloud). The platform’s RESTful APIs include data models for pricing and reference data.
- **Link**: [LSEG API Catalog](https://developers.lseg.com/en/api-catalog)

### 5. FXCM
- **System**: FXCM APIs (REST, FIX, Java, ForexConnect)
- **Description**: FXCM is a well-known FX broker that provides APIs for algorithmic trading and data access. Its APIs connect directly to the FXCM trading server, supporting real-time price updates and order execution.
- **Documentation and Data Models**: FXCM offers detailed API documentation, including specifications for its REST API, FIX API, and ForexConnect API. These documents define data models for trading orders, price data, and account information, available through their developer portal.
- **Link**: [FXCM API Docs](https://fxcm-api.readthedocs.io/en/latest/)

## Other Notable Vendors
The analysis also identified other vendors in the FX software market, but their documentation or data models were not as clearly accessible or publicly available:
- **TradingView**: Provides a popular charting platform for FX traders but lacks publicly available API documentation for data models.
- **Dukascopy**: Offers trading platforms and APIs, but documentation is often restricted to account holders.
- **Integral**: Specializes in FX technology for institutions, but public documentation is limited.
- **OANDA**: Provides FX trading platforms and APIs, but detailed documentation requires account access.
- **Finastra**: Offers treasury and FX management solutions, but public data models are not widely available.
- **Murex**: Provides sophisticated FX trading systems, but documentation is typically proprietary.
- **360T**: A multi-bank FX trading platform, but public documentation is limited compared to the listed vendors.
- **FIS (Global FX)**: Offers FX solutions for banks, but detailed documentation is not publicly accessible.
- **Apex Group (Monex Auto-FX)**: Provides automated FX trading, but public data models are not widely available.

These vendors may have documentation or data models available under specific conditions (e.g., licensing agreements), but they were not included in the table due to insufficient evidence of public access.

## Table of Vendors with Documentation
The following table summarizes the vendors with confirmed published data models or documentation, along with links to their resources:

| Vendor            | System            | Documentation Link                                                                 |
|-------------------|-------------------|------------------------------------------------------------------------------------|
| Bloomberg         | FXGO              | [Bloomberg Developer Portal](https://www.bloomberg.com/professional/support/api-library/) |
| MetaQuotes        | MetaTrader 4/5    | [MetaTrader Docs](https://www.mql5.com/en/docs)                                    |
| Saxo Bank         | SaxoOpenAPI       | [Saxo OpenAPI](https://www.developer.saxo/openapi/referencedocs)                   |
| Refinitiv (LSEG)  | Data Platform     | [LSEG API Catalog](https://developers.lseg.com/en/api-catalog)                     |
| FXCM              | FXCM APIs         | [FXCM API Docs](https://fxcm-api.readthedocs.io/en/latest/)                        |

## Limitations and Considerations
- **Accessibility**: Some vendors, like Bloomberg, may restrict full documentation to registered users or clients (e.g., Bloomberg Terminal subscribers), which could limit public access to data models.
- **Comprehensiveness**: The data models provided in API documentation may not cover all aspects of the system, depending on the vendor’s focus (e.g., trading vs. data analytics).
- **Updates**: Documentation may evolve, so users should check the vendor’s developer portal for the latest resources.
- **Additional Vendors**: Other vendors may offer FX systems with documentation, but they were not included due to limited evidence in the sources reviewed. Contacting vendors directly may reveal additional resources.
- **Nfino**: The lack of evidence for Nfino’s involvement in FX suggests it may not be a relevant vendor, but further details could prompt a re-evaluation.

## Recommendations
For users seeking FX systems with robust documentation:
- **Bloomberg (FXGO)** is ideal for institutional traders and buy-side firms needing multi-bank connectivity and advanced analytics, though documentation access may require a subscription.
- **MetaQuotes** is ideal for traders and developers building automated trading strategies, given its open MQL5 documentation.
- **Saxo Bank** suits those needing a flexible API for multi-asset trading platforms.
- **Refinitiv (LSEG)** is best for institutions requiring comprehensive FX data and analytics.
- **FXCM** is suitable for algorithmic traders looking for direct trading server access.

If you need information on other vendors, specific features, or clarification about Nfino, consider visiting their official websites or contacting their support teams for access to restricted documentation.

## Key Citations
- [Bloomberg FXGO Overview](https://www.bloomberg.com/professional/product/foreign-exchange-fxgo/)
- [Bloomberg Developer Portal](https://www.bloomberg.com/professional/support/api-library/)
- [Top 10 Foreign Exchange Software Companies - DataHorizzon Research](https://datahorizzonresearch.com/blog/top-10-foreign-exchange-software-companies-133)
- [MetaTrader MQL5 Documentation](https://www.mql5.com/en/docs)
- [Saxo Bank OpenAPI Reference Documentation](https://www.developer.saxo/openapi/referencedocs)
- [LSEG Developer Portal API Catalog](https://developers.lseg.com/en/api-catalog)
- [FXCM API Developer Documentation](https://fxcm-api.readthedocs.io/en/latest/)
