# Sorare GraphQL queries for Cards and Pricing

GET_CARDS_BY_PLAYER_QUERY = """
query GetCardsByPlayer($slug: String!, $first: Int!) {
  football {
    player(slug: $slug) {
      cards(first: $first) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          assetId
          season {
            startYear
          }
          rarity
          position
          power
          pictureUrl
          latestPrice {
            eur
            usd
            wei
          }
        }
      }
    }
  }
}
"""

GET_CARD_BY_ID_QUERY = """
query GetCardById($id: ID!) {
  football {
    card(id: $id) {
      id
      assetId
      rarity
      season {
        startYear
      }
      power
      pictureUrl
      player {
        id
        slug
        displayName
      }
      latestPrice {
        eur
        usd
        wei
      }
    }
  }
}
"""
