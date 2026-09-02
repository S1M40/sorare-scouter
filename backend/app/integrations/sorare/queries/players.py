# Sorare GraphQL queries for Players, Injuries, Suspensions, and Scores

GET_PLAYER_BY_SLUG_QUERY = """
query GetPlayerBySlug($slug: String!) {
  football {
    player(slug: $slug) {
      id
      slug
      displayName
      firstName
      lastName
      age
      position
      nationality {
        name
      }
      pictureUrl
      activeClub {
        id
        slug
        name
        shortName
        pictureUrl
        country {
          name
        }
      }
      activeInjuries {
        id
        active
        kind
        details
        startDate
        expectedEndDate
      }
      activeSuspensions {
        id
        active
        reason
        startDate
        endDate
      }
      lastFiveScores {
        score
      }
      lastFifteenScores {
        score
      }
    }
  }
}
"""

GET_PLAYERS_PAGINATED_QUERY = """
query GetPlayersPaginated($first: Int!, $after: String) {
  football {
    players(first: $first, after: $after) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        id
        slug
        displayName
        firstName
        lastName
        age
        position
        pictureUrl
        activeClub {
          id
          slug
          name
          pictureUrl
        }
      }
    }
  }
}
"""
