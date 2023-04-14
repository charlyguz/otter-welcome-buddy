from typing import Any


user_public_profile_schema: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "matchedUser": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "profile": {
                    "type": "object",
                    "properties": {
                        "countryName": {"type": ["string", "null"]},
                        "ranking": {"type": "number"},
                        "userAvatar": {"type": "string"},
                    },
                    "required": ["countryName"],
                    "additionalProperties": False,
                },
            },
            "required": ["username", "profile"],
            "additionalProperties": False,
        },
    },
    "required": ["matchedUser"],
    "additionalProperties": False,
}

user_recent_ac_submissions_schema: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "UserRecentAcSubmissions",
    "type": "object",
    "properties": {
        "recentAcSubmissionList": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "titleSlug": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
                "required": ["id", "titleSlug", "timestamp"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["recentAcSubmissionList"],
    "additionalProperties": False,
}

user_problem_solved_schema: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "UserProblemSolved",
    "type": "object",
    "properties": {
        "matchedUser": {
            "type": "object",
            "properties": {
                "submitStatsGlobal": {
                    "type": "object",
                    "properties": {
                        "acSubmissionNum": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "difficulty": {"type": "string"},
                                    "count": {"type": "number"},
                                },
                                "required": ["difficulty", "count"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["acSubmissionNum"],
                    "additionalProperties": False,
                },
            },
            "required": ["submitStatsGlobal"],
            "additionalProperties": False,
        },
        "question": {
            "type": "object",
            "properties": {
                "titleSlug": {"type": "string"},
                "questionId": {"type": "string"},
                "difficulty": {"type": "string"},
            },
            "required": ["questionId", "difficulty"],
            "additionalProperties": False,
        },
    },
    "required": ["matchedUser", "question"],
    "additionalProperties": False,
}
