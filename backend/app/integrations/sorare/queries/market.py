# Sorare GraphQL queries for Market Auctions and Offers

GET_ACTIVE_AUCTIONS_QUERY = """
query GetActiveAuctions($first: Int!) {
  football {
    tokenAuctions(first: $first) {
      nodes {
        id
        currentPrice {
          eur
          usd
          wei
        }
        endDate
        card {
          id
          rarity
          player {
            id
            slug
            displayName
          }
        }
      }
    }
  }
}
"""
