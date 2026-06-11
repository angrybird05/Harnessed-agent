import re


async def auto_apply(
    apply_url: str,
    user_profile: dict,
    resume_path: str,
    cover_letter: str,
) -> dict:
    """Automatically fill and submit a job application form using Playwright.

    Uses Chromium in headless mode to navigate to the apply URL,
    fill form fields by label matching, upload resume, and click submit.

    Returns:
        {success: bool, message: str}
    """
    from playwright.async_api import async_playwright

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto(apply_url, wait_until="networkidle", timeout=30000)

                # Parse user profile fields
                full_name = user_profile.get("full_name", "")
                name_parts = full_name.split(" ", 1) if full_name else ["", ""]
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = name_parts[1] if len(name_parts) > 1 else ""
                email = user_profile.get("email", "")
                phone = user_profile.get("phone", "")
                linkedin = user_profile.get("linkedin_url", "")
                website = user_profile.get("portfolio_url", "")

                # Fill fields by label matching
                field_mappings = [
                    ("first name", first_name),
                    ("last name", last_name),
                    ("email", email),
                    ("phone", phone),
                    ("linkedin", linkedin),
                    ("cover letter", cover_letter),
                    ("website", website),
                ]

                for label, value in field_mappings:
                    if not value:
                        continue
                    try:
                        # Try to find input by label
                        locator = page.get_by_label(label, exact=False)
                        if await locator.count() > 0:
                            await locator.first.fill(value)
                    except Exception:
                        pass

                # Upload resume to input[type="file"] if present
                try:
                    file_input = page.locator('input[type="file"]')
                    if await file_input.count() > 0:
                        await file_input.first.set_input_files(resume_path)
                except Exception:
                    pass

                # Click submit/apply button by role using regex for OR matching
                try:
                    submit_button = page.get_by_role(
                        "button",
                        name=re.compile(
                            r"submit|apply|send application", re.IGNORECASE
                        ),
                    )
                    if await submit_button.count() > 0:
                        await submit_button.first.click()
                        await page.wait_for_timeout(3000)
                    else:
                        # Fallback: try common button selectors
                        fallback = page.locator(
                            'button[type="submit"], input[type="submit"]'
                        )
                # FIX HIGH-06: Verify submission by checking if URL changed.
                # An unchanged URL strongly suggests the form was not submitted.
                pre_submit_url = page.url
                await page.wait_for_timeout(3000)
                post_submit_url = page.url

                if post_submit_url != pre_submit_url:
                    return {"success": True, "message": f"Application submitted — redirected to {post_submit_url}"}
                else:
                    return {"success": False, "message": "Submission may have failed — URL unchanged after submit"}

            finally:
                await browser.close()

    except Exception as e:
        return {"success": False, "message": f"Auto-apply failed: {str(e)}"}
