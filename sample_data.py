"""
Sample meeting transcript for testing the AI-Driven Meeting Summarizer
"""
import json
from datetime import datetime

# Sample meeting transcript
sample_transcript = """
Meeting: Weekly Product Development Review
Date: 2024-01-15
Attendees: Alice Johnson (Product Manager), Bob Smith (Lead Developer), Carol Davis (Designer), David Wilson (QA Lead)

Alice: Good morning everyone. Let's start with our weekly product development review. Bob, can you give us an update on the current sprint progress?

Bob: Sure, Alice. We've completed 8 out of 12 user stories for this sprint. The authentication module is fully implemented and tested. We're currently working on the payment integration feature, which is about 70% complete. However, we've encountered some issues with the third-party API that we need to resolve.

Alice: What kind of issues are we facing with the payment API?

Bob: The API documentation is incomplete, and we're getting inconsistent responses. We need to contact their support team to clarify the integration requirements. This might delay the payment feature by 2-3 days.

Carol: I've finished the UI mockups for the dashboard redesign. The new layout should improve user experience significantly. I've shared the designs with Bob for technical review.

Alice: Great work, Carol. Bob, can you review Carol's designs and provide feedback by Wednesday?

Bob: Absolutely, I'll review them by Wednesday and provide my technical assessment.

David: I've completed testing for the authentication module. All test cases are passing, and the security audit shows no vulnerabilities. I'm ready to start testing the payment integration once Bob completes the implementation.

Alice: Excellent. David, please prepare a comprehensive test plan for the payment feature. We need to ensure it's thoroughly tested before release.

David: I'll have the test plan ready by Friday and start testing as soon as the feature is available.

Alice: Now, let's discuss the upcoming release. We're targeting January 30th for the beta release. Bob, do you think we can meet this deadline?

Bob: Yes, if we resolve the payment API issues quickly. I'll contact their support today and get back to you with an update tomorrow.

Alice: Perfect. Carol, can you prepare the marketing materials for the beta release announcement?

Carol: I'll work on the marketing materials this week and have them ready by next Monday.

Alice: One more thing - we need to schedule user interviews for next week to gather feedback on the new features. Carol, can you coordinate with the user research team?

Carol: I'll reach out to them today and schedule the interviews for next week.

Alice: Great. Let's wrap up here. Bob, please send me an update on the payment API issue by tomorrow. David, continue with the test plan preparation. Carol, work on the marketing materials and user interviews. Any questions?

Bob: No questions from my side.

Carol: All clear.

David: I'm good to go.

Alice: Perfect. Meeting adjourned. Have a great week everyone!
"""

# Sample JSON transcript format
sample_json_transcript = {
    "meeting_title": "Weekly Product Development Review",
    "date": "2024-01-15",
    "attendees": [
        {"name": "Alice Johnson", "role": "Product Manager"},
        {"name": "Bob Smith", "role": "Lead Developer"},
        {"name": "Carol Davis", "role": "Designer"},
        {"name": "David Wilson", "role": "QA Lead"}
    ],
    "transcript": sample_transcript,
    "duration_minutes": 25,
    "meeting_type": "weekly_review"
}

# Sample action items (what the AI should extract)
expected_action_items = [
    {
        "task": "Contact payment API support team to resolve integration issues",
        "assignee": "Bob Smith",
        "priority": "high",
        "context": "API documentation incomplete, inconsistent responses"
    },
    {
        "task": "Review Carol's dashboard UI designs and provide technical feedback",
        "assignee": "Bob Smith",
        "priority": "medium",
        "context": "Due by Wednesday"
    },
    {
        "task": "Prepare comprehensive test plan for payment feature",
        "assignee": "David Wilson",
        "priority": "medium",
        "context": "Due by Friday"
    },
    {
        "task": "Prepare marketing materials for beta release announcement",
        "assignee": "Carol Davis",
        "priority": "medium",
        "context": "Due by next Monday"
    },
    {
        "task": "Coordinate with user research team to schedule user interviews",
        "assignee": "Carol Davis",
        "priority": "medium",
        "context": "Schedule for next week"
    },
    {
        "task": "Send update on payment API issue to Alice",
        "assignee": "Bob Smith",
        "priority": "high",
        "context": "Due tomorrow"
    }
]

# Sample summary (what the AI should generate)
expected_summary = """
The weekly product development review covered sprint progress, technical challenges, and upcoming release planning. The team has completed 8 out of 12 user stories, with the authentication module fully implemented and tested. The payment integration feature is 70% complete but faces API documentation issues that may cause a 2-3 day delay.

Key decisions made include targeting January 30th for the beta release, pending resolution of payment API issues. The team assigned specific action items: Bob will contact payment API support and review UI designs, David will prepare test plans, and Carol will handle marketing materials and user interviews.

The meeting emphasized the importance of resolving technical blockers quickly to maintain the release timeline, with clear ownership and deadlines established for each action item.
"""

def create_sample_files():
    """Create sample files for testing"""
    
    # Create sample text file
    with open('sample_meeting.txt', 'w', encoding='utf-8') as f:
        f.write(sample_transcript)
    
    # Create sample JSON file
    with open('sample_meeting.json', 'w', encoding='utf-8') as f:
        json.dump(sample_json_transcript, f, indent=2, ensure_ascii=False)
    
    print("Sample files created:")
    print("- sample_meeting.txt")
    print("- sample_meeting.json")
    print("\nExpected action items:")
    for i, item in enumerate(expected_action_items, 1):
        print(f"{i}. {item['task']} (Assignee: {item['assignee']}, Priority: {item['priority']})")

if __name__ == "__main__":
    create_sample_files()
