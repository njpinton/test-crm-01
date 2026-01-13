"""
End-to-end tests for Schedule and Comments functionality using Playwright.
Tests the new features: Schedule events, Comments, Site Officer, and Project Manager.
"""
import sys
import time
from playwright.sync_api import sync_playwright, expect


BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "admin@example.com"
TEST_USER_PASSWORD = "admin123"


def remove_debug_toolbar(page):
    """Completely remove Django Debug Toolbar to prevent click interception."""
    page.evaluate("""
        const toolbar = document.getElementById('djDebug');
        if (toolbar) {
            toolbar.remove();
        }
        document.querySelectorAll('[id^="djDebug"], [id^="djdt"], .djdt-hidden').forEach(el => el.remove());
    """)


def login(page):
    """Helper function to log in to the CRM."""
    page.goto(f"{BASE_URL}/accounts/login/", timeout=10000)
    page.wait_for_load_state("domcontentloaded")
    page.fill('input[name="login"]', TEST_USER_EMAIL)
    page.fill('input[name="password"]', TEST_USER_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    remove_debug_toolbar(page)
    return "login" not in page.url


def ensure_test_client_exists(page):
    """Ensure a test client exists for creating deals."""
    page.goto(f"{BASE_URL}/clients/")
    page.wait_for_load_state("networkidle")
    remove_debug_toolbar(page)

    if not page.locator('text=Schedule Test Client').first.is_visible():
        page.goto(f"{BASE_URL}/clients/create/")
        page.wait_for_load_state("networkidle")
        remove_debug_toolbar(page)
        page.wait_for_timeout(300)
        page.fill('input[name="company_name"]', "Schedule Test Client")
        page.fill('input[name="contact_name"]', "Schedule Contact")
        page.fill('input[name="contact_email"]', "schedule@test.com")
        submit_btn = page.locator('main button[type="submit"]').first
        submit_btn.click(force=True)
        page.wait_for_load_state("networkidle")
        remove_debug_toolbar(page)
        print("  INFO: Test client created")
    else:
        print("  INFO: Test client already exists")


def create_test_deal(page):
    """Create a test deal and return its URL."""
    page.goto(f"{BASE_URL}/pipeline/deals/create/")
    page.wait_for_load_state("networkidle")
    remove_debug_toolbar(page)
    page.wait_for_timeout(300)

    # Fill in deal form
    timestamp = int(time.time())
    deal_title = f"Schedule Test Deal {timestamp}"
    page.fill('input[name="title"]', deal_title)
    page.fill('textarea[name="description"]', "Test deal for schedule and comments testing.")

    # Select client
    client_select = page.locator('select[name="client"]')
    options = client_select.locator('option')
    for i in range(options.count()):
        option = options.nth(i)
        if "Schedule Test Client" in option.inner_text():
            client_select.select_option(index=i)
            break

    # Fill financial info
    page.fill('input[name="estimated_value"]', "25000")
    page.fill('input[name="probability"]', "50")

    # Submit form
    submit_btn = page.locator('main form button[type="submit"]').first
    submit_btn.click(force=True)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)
    remove_debug_toolbar(page)

    return page.url, deal_title


def test_deal_form_new_fields():
    """Test that Site Officer and Project Manager fields appear in the deal form."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 60)
        print("DEAL FORM NEW FIELDS TESTS")
        print("=" * 60)

        # Login first
        print("\n[SETUP] Logging in...")
        if not login(page):
            print("  FAIL: Could not log in")
            browser.close()
            return False
        print("  PASS: Logged in successfully")

        # Navigate to create deal page
        print("\n[TEST 1] Site Officer field in form...")
        page.goto(f"{BASE_URL}/pipeline/deals/create/")
        page.wait_for_load_state("networkidle")
        remove_debug_toolbar(page)

        site_officer_field = page.locator('select[name="site_officer"]')
        assert site_officer_field.is_visible(), "Site Officer field not found"
        print("  PASS: Site Officer field present")

        print("\n[TEST 2] Project Manager field in form...")
        project_manager_field = page.locator('select[name="project_manager"]')
        assert project_manager_field.is_visible(), "Project Manager field not found"
        print("  PASS: Project Manager field present")

        print("\n[TEST 3] Field labels are correct...")
        site_officer_label = page.locator('label:has-text("Site Officer")')
        project_manager_label = page.locator('label:has-text("Project Manager")')
        assert site_officer_label.is_visible()
        assert project_manager_label.is_visible()
        print("  PASS: Field labels are correct")

        # Take screenshot
        page.screenshot(path="tests/deal_form_new_fields.png")
        print("  INFO: Screenshot saved to tests/deal_form_new_fields.png")

        browser.close()

        print("\n" + "=" * 60)
        print("DEAL FORM NEW FIELDS TESTS PASSED")
        print("=" * 60)

        return True


def test_deal_detail_schedule_section():
    """Test that Schedule section appears on deal detail page."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 60)
        print("DEAL DETAIL SCHEDULE SECTION TESTS")
        print("=" * 60)

        # Login first
        print("\n[SETUP] Logging in...")
        if not login(page):
            print("  FAIL: Could not log in")
            browser.close()
            return False
        print("  PASS: Logged in successfully")

        # Ensure test client exists
        print("\n[SETUP] Ensuring test client exists...")
        ensure_test_client_exists(page)

        # Create a test deal
        print("\n[SETUP] Creating test deal...")
        deal_url, deal_title = create_test_deal(page)
        print(f"  INFO: Deal created: {deal_title}")

        # Navigate to deal detail
        print("\n[TEST 1] Schedule section on deal detail...")
        page.goto(deal_url)
        page.wait_for_load_state("networkidle")
        remove_debug_toolbar(page)

        # Use exact match to avoid ambiguity with "No scheduled events" heading
        schedule_section = page.get_by_role("heading", name="Schedule", exact=True)
        assert schedule_section.is_visible(), "Schedule section not found"
        print("  PASS: Schedule section present")

        print("\n[TEST 2] Add Event button present...")
        add_event_btn = page.locator('button:has-text("Add Event")')
        assert add_event_btn.is_visible(), "Add Event button not found"
        print("  PASS: Add Event button present")

        print("\n[TEST 3] Comments section present...")
        # Use exact match to avoid ambiguity with "No comments yet" heading
        comments_section = page.get_by_role("heading", name="Comments", exact=True)
        assert comments_section.is_visible(), "Comments section not found"
        print("  PASS: Comments section present")

        # Take screenshot
        page.screenshot(path="tests/deal_detail_schedule.png")
        print("  INFO: Screenshot saved to tests/deal_detail_schedule.png")

        browser.close()

        print("\n" + "=" * 60)
        print("DEAL DETAIL SCHEDULE SECTION TESTS PASSED")
        print("=" * 60)

        return True


def test_add_schedule_event():
    """Test adding a schedule event to a deal."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 60)
        print("ADD SCHEDULE EVENT TESTS")
        print("=" * 60)

        # Login first
        print("\n[SETUP] Logging in...")
        if not login(page):
            print("  FAIL: Could not log in")
            browser.close()
            return False
        print("  PASS: Logged in successfully")

        # Ensure test client exists
        print("\n[SETUP] Ensuring test client exists...")
        ensure_test_client_exists(page)

        # Create a test deal
        print("\n[SETUP] Creating test deal...")
        deal_url, deal_title = create_test_deal(page)
        print(f"  INFO: Deal created: {deal_title}")

        # Navigate to deal detail
        page.goto(deal_url)
        page.wait_for_load_state("networkidle")
        remove_debug_toolbar(page)

        print("\n[TEST 1] Open schedule modal...")
        add_event_btn = page.locator('button:has-text("Add Event")')
        add_event_btn.click()
        page.wait_for_timeout(500)  # Wait for modal and HTMX to load

        # Wait for modal content to load
        modal_content = page.locator('#schedule-modal-content')
        assert modal_content.is_visible(), "Schedule modal not visible"
        print("  PASS: Schedule modal opened")

        print("\n[TEST 2] Fill schedule form...")
        page.wait_for_timeout(300)

        # Fill in the schedule form
        page.locator('select[name="event_type"]').select_option("SITE_VISIT")
        page.fill('input[name="title"]', "Initial Site Assessment")
        page.fill('textarea[name="description"]', "Assess current fire protection systems")
        page.fill('input[name="scheduled_date"]', "2025-02-15")
        page.fill('input[name="scheduled_time"]', "10:00")
        page.fill('input[name="duration_hours"]', "2")
        page.fill('textarea[name="location_notes"]', "Main building, floor 3")
        page.fill('textarea[name="access_instructions"]', "Check in at reception")
        page.fill('textarea[name="equipment_needed"]', "Inspection kit, camera")

        print("  PASS: Form filled")

        print("\n[TEST 3] Submit schedule form...")
        submit_btn = page.locator('#schedule-modal-content button[type="submit"]')
        submit_btn.click()
        page.wait_for_timeout(1000)  # Wait for HTMX to update

        # Check if the schedule appears in the list
        page.wait_for_timeout(500)
        schedule_item = page.locator('text=Initial Site Assessment')
        assert schedule_item.is_visible(), "Schedule not created or not visible"
        print("  PASS: Schedule event created successfully")

        # Take screenshot
        page.screenshot(path="tests/schedule_added.png")
        print("  INFO: Screenshot saved to tests/schedule_added.png")

        browser.close()

        print("\n" + "=" * 60)
        print("ADD SCHEDULE EVENT TESTS PASSED")
        print("=" * 60)

        return True


def test_add_comment():
    """Test adding a comment to a deal."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 60)
        print("ADD COMMENT TESTS")
        print("=" * 60)

        # Login first
        print("\n[SETUP] Logging in...")
        if not login(page):
            print("  FAIL: Could not log in")
            browser.close()
            return False
        print("  PASS: Logged in successfully")

        # Ensure test client exists
        print("\n[SETUP] Ensuring test client exists...")
        ensure_test_client_exists(page)

        # Create a test deal
        print("\n[SETUP] Creating test deal...")
        deal_url, deal_title = create_test_deal(page)
        print(f"  INFO: Deal created: {deal_title}")

        # Navigate to deal detail
        page.goto(deal_url)
        page.wait_for_load_state("networkidle")
        remove_debug_toolbar(page)

        print("\n[TEST 1] Comment form present...")
        comment_textarea = page.locator('#comments-section textarea[name="content"]')
        assert comment_textarea.is_visible(), "Comment textarea not found"
        print("  PASS: Comment form present")

        print("\n[TEST 2] Add a comment...")
        comment_text = "This is a test comment for the deal. Need to schedule site visit."
        comment_textarea.fill(comment_text)

        submit_btn = page.locator('#comments-section button[type="submit"]')
        submit_btn.click()
        page.wait_for_timeout(1000)  # Wait for HTMX to update

        print("\n[TEST 3] Verify comment appears...")
        page.wait_for_timeout(500)
        comment_content = page.locator(f'text={comment_text[:30]}')
        assert comment_content.is_visible(), "Comment not visible after submission"
        print("  PASS: Comment added successfully")

        # Take screenshot
        page.screenshot(path="tests/comment_added.png")
        print("  INFO: Screenshot saved to tests/comment_added.png")

        browser.close()

        print("\n" + "=" * 60)
        print("ADD COMMENT TESTS PASSED")
        print("=" * 60)

        return True


def test_team_display():
    """Test that Site Officer and Project Manager display on deal detail."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("=" * 60)
        print("TEAM DISPLAY TESTS")
        print("=" * 60)

        # Login first
        print("\n[SETUP] Logging in...")
        if not login(page):
            print("  FAIL: Could not log in")
            browser.close()
            return False
        print("  PASS: Logged in successfully")

        # Ensure test client exists
        print("\n[SETUP] Ensuring test client exists...")
        ensure_test_client_exists(page)

        # Create a deal with site officer and project manager assigned
        print("\n[SETUP] Creating test deal with team assignments...")
        page.goto(f"{BASE_URL}/pipeline/deals/create/")
        page.wait_for_load_state("networkidle")
        remove_debug_toolbar(page)
        page.wait_for_timeout(300)

        timestamp = int(time.time())
        deal_title = f"Team Test Deal {timestamp}"
        page.fill('input[name="title"]', deal_title)

        # Select client
        client_select = page.locator('select[name="client"]')
        options = client_select.locator('option')
        for i in range(options.count()):
            option = options.nth(i)
            if "Schedule Test Client" in option.inner_text():
                client_select.select_option(index=i)
                break

        page.fill('input[name="estimated_value"]', "30000")

        # Try to select site officer and project manager (if users exist)
        site_officer_select = page.locator('select[name="site_officer"]')
        so_options = site_officer_select.locator('option')
        if so_options.count() > 1:  # Has options besides empty
            site_officer_select.select_option(index=1)  # Select first user
            print("  INFO: Site officer selected")

        pm_select = page.locator('select[name="project_manager"]')
        pm_options = pm_select.locator('option')
        if pm_options.count() > 1:
            pm_select.select_option(index=1)  # Select first user
            print("  INFO: Project manager selected")

        # Submit form
        submit_btn = page.locator('main form button[type="submit"]').first
        submit_btn.click(force=True)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)
        remove_debug_toolbar(page)

        deal_url = page.url
        print(f"  INFO: Deal created at {deal_url}")

        print("\n[TEST 1] Team section on deal detail...")
        team_section = page.locator('h3:has-text("Team")')
        assert team_section.is_visible(), "Team section not found"
        print("  PASS: Team section present")

        print("\n[TEST 2] Owner displayed...")
        owner_label = page.locator('dt:has-text("Owner")')
        assert owner_label.is_visible(), "Owner label not found"
        print("  PASS: Owner displayed")

        # Take screenshot
        page.screenshot(path="tests/team_display.png")
        print("  INFO: Screenshot saved to tests/team_display.png")

        browser.close()

        print("\n" + "=" * 60)
        print("TEAM DISPLAY TESTS PASSED")
        print("=" * 60)

        return True


def run_all_tests():
    """Run all schedule and comments e2e tests."""
    print("\n" + "=" * 70)
    print("  SCHEDULE & COMMENTS E2E TEST SUITE")
    print("=" * 70)

    results = {}

    tests = [
        ("Deal Form New Fields", test_deal_form_new_fields),
        ("Deal Detail Schedule Section", test_deal_detail_schedule_section),
        ("Add Schedule Event", test_add_schedule_event),
        ("Add Comment", test_add_comment),
        ("Team Display", test_team_display),
    ]

    for test_name, test_func in tests:
        try:
            print(f"\n{'='*70}")
            print(f"  Running: {test_name}")
            print("=" * 70)
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n  FAIL: {test_name} - {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Print summary
    print("\n" + "=" * 70)
    print("  TEST SUITE SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {test_name}")

    print("\n" + "-" * 70)
    print(f"  Total: {passed}/{total} tests passed")
    print("=" * 70)

    return all(results.values())


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nTEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
