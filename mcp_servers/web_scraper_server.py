"""
Web Scraper MCP Server — Exposes tools for scraping Kaggle competition pages.

Tools:
  - scrape_competition_page(url): Fetches and parses competition overview,
    evaluation metric, data description, and rules.
  - search_discussions(url): Retrieves top discussion posts with tips,
    winning solutions, and common mistakes.

This is an MCP server that agents call via the MCP protocol. Each tool
returns structured data that agents can reason about.
"""

import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup


def _fetch_page(url: str, timeout: int = 15) -> str:
    """Fetches HTML content from a URL with error handling."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"ERROR: Failed to fetch {url}: {str(e)}"


def _clean_text(text: str) -> str:
    """Cleans extracted text by removing excess whitespace."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_competition_slug(url: str) -> str:
    """Extracts the competition slug from a Kaggle URL."""
    # Handle URLs like:
    # https://www.kaggle.com/competitions/titanic
    # https://www.kaggle.com/competitions/titanic/overview
    # https://www.kaggle.com/c/titanic
    match = re.search(r"kaggle\.com/(?:competitions|c)/([^/?\s]+)", url)
    if match:
        return match.group(1)
    return url  # Return as-is if pattern doesn't match


def _parse_kaggle_api_response(slug: str) -> dict[str, Any]:
    """
    Fetches competition metadata via Kaggle's public-facing endpoints.
    Falls back to HTML scraping if the API is unavailable.
    """
    metadata = {
        "slug": slug,
        "title": "",
        "description": "",
        "evaluation_metric": "",
        "data_description": "",
        "rules_summary": "",
        "deadline": "",
        "competition_type": "",
        "url": f"https://www.kaggle.com/competitions/{slug}",
    }

    # Try fetching the overview page
    overview_html = _fetch_page(
        f"https://www.kaggle.com/competitions/{slug}/overview"
    )
    if overview_html.startswith("ERROR:"):
        # Fallback: try the legacy URL format
        overview_html = _fetch_page(f"https://www.kaggle.com/c/{slug}/overview")

    if not overview_html.startswith("ERROR:"):
        soup = BeautifulSoup(overview_html, "html.parser")

        # Extract title from page title or meta tags
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text()
            # Remove " | Kaggle" suffix
            metadata["title"] = title_text.replace(" | Kaggle", "").strip()

        # Extract meta description
        meta_desc = soup.find("meta", {"name": "description"})
        if meta_desc:
            metadata["description"] = meta_desc.get("content", "")

        # Extract OG description (often more detailed)
        og_desc = soup.find("meta", {"property": "og:description"})
        if og_desc:
            og_content = og_desc.get("content", "")
            if len(og_content) > len(metadata["description"]):
                metadata["description"] = og_content

        # Try to extract content from script tags (Kaggle stores data in JSON)
        scripts = soup.find_all("script")
        for script in scripts:
            script_text = script.string or ""
            # Look for competition data embedded in JavaScript
            if "competitionData" in script_text or "Kaggle.State" in script_text:
                # Try to extract JSON data
                json_match = re.search(
                    r"(?:competitionData|Kaggle\.State\.push\()\s*({.*?})\s*[;)]",
                    script_text,
                    re.DOTALL,
                )
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                        if isinstance(data, dict):
                            metadata["title"] = data.get(
                                "title", metadata["title"]
                            )
                            metadata["evaluation_metric"] = data.get(
                                "evaluationMetric", ""
                            )
                            metadata["deadline"] = data.get("deadline", "")
                    except json.JSONDecodeError:
                        pass

    # Try fetching the data description page
    data_html = _fetch_page(
        f"https://www.kaggle.com/competitions/{slug}/data"
    )
    if not data_html.startswith("ERROR:"):
        soup = BeautifulSoup(data_html, "html.parser")
        # Look for data description content
        data_sections = soup.find_all(["p", "li", "h2", "h3"])
        data_text_parts = []
        for section in data_sections[:20]:  # Limit to first 20 elements
            text = _clean_text(section.get_text())
            if text and len(text) > 10:
                data_text_parts.append(text)
        if data_text_parts:
            metadata["data_description"] = "\n".join(data_text_parts[:10])

    # Infer competition type from metadata
    title_lower = metadata["title"].lower()
    desc_lower = metadata["description"].lower()
    combined = title_lower + " " + desc_lower

    if any(
        word in combined
        for word in ["classification", "classify", "predict whether", "binary"]
    ):
        metadata["competition_type"] = "classification"
    elif any(
        word in combined
        for word in ["regression", "predict the value", "forecast", "price"]
    ):
        metadata["competition_type"] = "regression"
    elif any(
        word in combined
        for word in [
            "nlp",
            "text",
            "sentiment",
            "language",
            "translation",
        ]
    ):
        metadata["competition_type"] = "nlp"
    elif any(
        word in combined
        for word in ["image", "vision", "detection", "segmentation"]
    ):
        metadata["competition_type"] = "computer_vision"
    else:
        metadata["competition_type"] = "unknown"

    return metadata


def scrape_competition_page(url: str) -> dict[str, Any]:
    """
    Scrapes a Kaggle competition page and returns structured metadata.

    Args:
        url: The Kaggle competition URL
            (e.g., 'https://www.kaggle.com/competitions/titanic')

    Returns:
        A dictionary containing:
        - slug: Competition identifier
        - title: Competition title
        - description: Competition description/overview
        - evaluation_metric: How submissions are scored
        - data_description: Description of the dataset
        - rules_summary: Key rules
        - deadline: Submission deadline
        - competition_type: Inferred type (classification, regression, etc.)
        - url: Full competition URL
    """
    slug = _extract_competition_slug(url)
    metadata = _parse_kaggle_api_response(slug)

    # If we couldn't extract much from the page (Kaggle is a SPA),
    # provide a helpful fallback with the slug-based inference
    if not metadata["title"] or metadata["title"] == slug:
        # Use the slug to create a readable title
        metadata["title"] = slug.replace("-", " ").title()
        metadata["description"] = (
            f"Competition '{slug}' on Kaggle. "
            "Note: Full details could not be automatically extracted. "
            "The page may require JavaScript rendering. "
            "Please provide additional context about this competition."
        )

    return metadata


def search_discussions(url: str, max_posts: int = 5) -> dict[str, Any]:
    """
    Searches a Kaggle competition's discussion tab for useful posts.

    Looks for posts about winning strategies, common pitfalls,
    starter notebooks, and tips from experienced competitors.

    Args:
        url: The Kaggle competition URL
        max_posts: Maximum number of posts to return (default 5)

    Returns:
        A dictionary containing:
        - posts: List of discussion post summaries
        - total_found: Number of posts found
        - search_url: URL of the discussions page
    """
    slug = _extract_competition_slug(url)
    discussions_url = f"https://www.kaggle.com/competitions/{slug}/discussion"

    result = {
        "posts": [],
        "total_found": 0,
        "search_url": discussions_url,
    }

    html = _fetch_page(discussions_url)
    if html.startswith("ERROR:"):
        result["posts"].append(
            {
                "title": "Could not fetch discussions",
                "summary": html,
                "votes": 0,
                "author": "system",
            }
        )
        return result

    soup = BeautifulSoup(html, "html.parser")

    # Kaggle discussions are rendered via React, so we try to find
    # any server-rendered content or embedded JSON data
    # Look for discussion titles in common HTML patterns
    post_elements = soup.find_all("a", href=re.compile(r"/discussion/\d+"))

    seen_titles = set()
    for element in post_elements:
        title = _clean_text(element.get_text())
        if title and title not in seen_titles and len(title) > 5:
            seen_titles.add(title)
            result["posts"].append(
                {
                    "title": title,
                    "summary": "",
                    "votes": 0,
                    "author": "",
                    "url": f"https://www.kaggle.com{element.get('href', '')}",
                }
            )

        if len(result["posts"]) >= max_posts:
            break

    # If we couldn't extract posts (SPA rendering), provide guidance
    if not result["posts"]:
        result["posts"].append(
            {
                "title": "Discussions not available via scraping",
                "summary": (
                    "Kaggle renders discussions via JavaScript. "
                    "For a full analysis, the user should manually review "
                    f"the discussions at {discussions_url}. "
                    "Key things to look for: winning solution summaries, "
                    "feature engineering tips, common mistakes, "
                    "and starter notebook recommendations."
                ),
                "votes": 0,
                "author": "system",
            }
        )

    result["total_found"] = len(result["posts"])
    return result


# Well-known competition metadata for reliable demos
# This provides a fallback when web scraping fails (Kaggle is a SPA)
KNOWN_COMPETITIONS = {
    "titanic": {
        "slug": "titanic",
        "title": "Titanic - Machine Learning from Disaster",
        "description": (
            "Predict which passengers survived the Titanic shipwreck. "
            "This is a binary classification competition and a great "
            "starting point for machine learning beginners."
        ),
        "evaluation_metric": "Accuracy (percentage of correct predictions)",
        "data_description": (
            "Training set: 891 passengers with 12 features including "
            "PassengerId, Survived (target), Pclass, Name, Sex, Age, "
            "SibSp, Parch, Ticket, Fare, Cabin, Embarked. "
            "Test set: 418 passengers (same features minus Survived)."
        ),
        "rules_summary": (
            "Standard Kaggle competition rules. "
            "Maximum 10 submissions per day."
        ),
        "deadline": "No deadline (ongoing Getting Started competition)",
        "competition_type": "classification",
        "url": "https://www.kaggle.com/competitions/titanic",
        "discussion_insights": [
            {
                "title": "Feature Engineering is Key",
                "summary": (
                    "Top solutions emphasize feature engineering over model "
                    "complexity. Key features to create: Title extraction "
                    "from Name (Mr, Mrs, Master, Miss), Family Size "
                    "(SibSp + Parch + 1), IsAlone flag, Fare bins, "
                    "Age bins, Cabin deck extraction."
                ),
            },
            {
                "title": "Best Models for Titanic",
                "summary": (
                    "Gradient boosting models (XGBoost, LightGBM) and "
                    "Random Forest typically perform best. Simple logistic "
                    "regression can achieve ~0.77. Ensemble methods can "
                    "push to 0.80+. Neural networks tend to overfit on "
                    "this small dataset."
                ),
            },
            {
                "title": "Common Pitfalls",
                "summary": (
                    "1) Not handling missing values in Age (20%) and "
                    "Cabin (77%). 2) Not encoding categorical features. "
                    "3) Overfitting to training data. 4) Ignoring the "
                    "Name column (it contains titles). 5) Not using "
                    "cross-validation."
                ),
            },
        ],
    },
    "house-prices-advanced-regression-techniques": {
        "slug": "house-prices-advanced-regression-techniques",
        "title": "House Prices - Advanced Regression Techniques",
        "description": (
            "Predict sales prices for residential homes in Ames, Iowa. "
            "This is a regression competition with 79 explanatory variables."
        ),
        "evaluation_metric": "RMSLE (Root Mean Squared Logarithmic Error)",
        "data_description": (
            "Training set: 1460 houses with 79 features covering "
            "lot size, neighborhood, building type, quality ratings, "
            "square footage, basement details, garage details, and more. "
            "Target: SalePrice (continuous, right-skewed)."
        ),
        "rules_summary": "Standard rules. 5 submissions per day.",
        "deadline": "No deadline (ongoing Getting Started competition)",
        "competition_type": "regression",
        "url": (
            "https://www.kaggle.com/competitions/"
            "house-prices-advanced-regression-techniques"
        ),
        "discussion_insights": [
            {
                "title": "Log Transform the Target",
                "summary": (
                    "SalePrice is right-skewed. Apply log1p transform "
                    "before training and expm1 when predicting. This "
                    "aligns with the RMSLE metric."
                ),
            },
            {
                "title": "Feature Engineering Strategies",
                "summary": (
                    "Create: TotalSF (total square footage), "
                    "TotalBathrooms, HouseAge, RemodAge. "
                    "Handle ordinal features (quality ratings) as numeric. "
                    "Remove outliers (GrLivArea > 4000)."
                ),
            },
        ],
    },
    "spaceship-titanic": {
        "slug": "spaceship-titanic",
        "title": "Spaceship Titanic",
        "description": (
            "Predict which passengers were transported to an alternate "
            "dimension during the Spaceship Titanic's collision with a "
            "spacetime anomaly. Binary classification."
        ),
        "evaluation_metric": "Classification Accuracy",
        "data_description": (
            "Training set: ~8700 passengers with features including "
            "HomePlanet, CryoSleep, Cabin (deck/num/side), Destination, "
            "Age, VIP, RoomService, FoodCourt, ShoppingMall, Spa, "
            "VRDeck, Name. Target: Transported (True/False)."
        ),
        "rules_summary": "Standard rules. 5 submissions per day.",
        "deadline": "No deadline (ongoing Getting Started competition)",
        "competition_type": "classification",
        "url": "https://www.kaggle.com/competitions/spaceship-titanic",
        "discussion_insights": [
            {
                "title": "Similar to Original Titanic",
                "summary": (
                    "Shares DNA with the Titanic competition. "
                    "Tree-based models work well. Key: parse Cabin into "
                    "deck, num, side. CryoSleep is a strong predictor. "
                    "Spending features (RoomService, etc.) are important."
                ),
            },
        ],
    },
}


def get_known_competition(slug: str) -> dict[str, Any] | None:
    """Returns pre-cached metadata for well-known competitions."""
    return KNOWN_COMPETITIONS.get(slug)
