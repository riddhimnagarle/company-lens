CompanyLens — Fallback Dataset
Company: Ghost (ghost.org) — open-source publishing platform
Scraped: 2026-09-20
Purpose: safety net for Section 10 of the project brief. Use only if your own
scraper isn't producing usable data by end of Day 2.

Files:
  metadata.json                              -- source_url, page_type, scrape_date, title per file
  about.txt                                  -- About page
  blog_how_to_publish_your_first_post.txt    -- Blog / resources article
  blog_build_audience_subscriber_signups.txt -- Blog / resources article
  careers.txt                                -- Careers page (careers.ghost.org)
  news_changelog.txt                         -- Product changelog (used as the "News" page type)

Each .txt file has a small header (SOURCE_URL / PAGE_TYPE / SCRAPE_DATE / TITLE)
followed by the cleaned page text, exactly the shape your own scraper's output
should take before cleaning/chunking/embedding.

Fetched respecting ghost.org's robots.txt (general crawl allowed), with delays
between requests and a standard browser user-agent. No login, no paywall, no
rate-limit abuse.
