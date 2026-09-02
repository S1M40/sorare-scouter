# Sorare GraphQL queries for SO5 Fixtures and Games

GET_SO5_FIXTURES_QUERY = """
query GetSO5Fixtures {
  football {
    so5Fixtures {
      id
      gameWeek
      startDate
      endDate
      cutoffDate
      state
    }
  }
}
"""

GET_GAMES_BY_DATE_QUERY = """
query GetGamesByDate($from: ISO8601DateTime!, $to: ISO8601DateTime!) {
  football {
    games(from: $from, to: $to) {
      id
      date
      status
      homeScore
      awayScore
      minute
      homeClub {
        id
        slug
        name
        pictureUrl
      }
      awayClub {
        id
        slug
        name
        pictureUrl
      }
      competition {
        id
        slug
        name
      }
    }
  }
}
"""
