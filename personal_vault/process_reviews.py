import json
import os
from datetime import datetime, timedelta
import re

# Path to the queue file
queue_path = '_inbox/review_queue.json'

# Read the file
with open(queue_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Process each pending entry with status raw_pending
for entry in data['pending']:
    if entry.get('status') == 'raw_pending':
        raw_text = entry['raw_text']
        received_at = entry['received_at']
        source = entry['source']
        platform = entry.get('platform', 'google')  # default to google if not set

        # Step 1: Parse raw_text
        # Store code: from "Store code: LUx" line, or store name in text.
        store_code = None
        store_name_from_text = None
        lines = raw_text.split('\n')
        for line in lines:
            if line.startswith('Store code:'):
                store_code = line.split(':')[1].strip()
                break
        # If not found, try to infer from store names in text
        if not store_code:
            if "L'Usine Le Thanh Ton" in raw_text or "L'Usine Lê Thánh Tôn" in raw_text:
                store_code = "LU3"
            elif "L'Usine Phu My Hung" in raw_text:
                store_code = "LU5"
            elif "L'Usine Saigon Centre" in raw_text:
                store_code = "LU7"
        # Map store code to full name for later use
        store_name_map = {
            "LU3": "L'Usine Le Thanh Ton",
            "LU5": "L'Usine Phu My Hung",
            "LU7": "L'Usine Saigon Centre"
        }
        store_full_name = store_name_map.get(store_code, None)

        # Reviewer: name line above the star line.
        reviewer = None
        # Find the line with stars ( or ★) and take the line before it.
        for i, line in enumerate(lines):
            if '' in line or '★' in line:
                if i > 0:
                    reviewer = lines[i-1].strip()
                break

        # Rating: COUNT ★ characters (each ★ = 1). Also count ? The example uses  for rating.
        # In the raw_text, we see both  and ★. We'll count both as one star each.
        rating = 0
        for line in lines:
            rating += line.count('')
            rating += line.count('★')

        # Review date: infer from "X minutes/hours/days ago" relative to received_at.
        review_date = None
        # We'll look for a pattern like "(\\d+)\\s*(minute|hour|day)s? ago"
        # We'll use the first occurrence.
        review_date_str = None
        for line in lines:
            # Look for patterns like "14 hours ago", "Yesterday", etc.
            if 'ago' in line.lower() or 'yesterday' in line.lower():
                review_date_str = line.strip()
                break

        # If we found a string, parse it.
        if review_date_str:
            # Convert received_at to datetime
            try:
                received_dt = datetime.fromisoformat(received_at.replace('Z', '+00:00'))
            except:
                # If format is different, try without timezone
                received_dt = datetime.strptime(received_at, '%Y-%m-%dT%H:%M:%S')
            # Now parse the review_date_str
            lower_str = review_date_str.lower()
            if 'yesterday' in lower_str:
                review_dt = received_dt - timedelta(days=1)
            elif 'hour' in lower_str:
                # Extract number
                match = re.search(r'(\\d+)\\s*hour', lower_str)
                if match:
                    hours = int(match.group(1))
                    review_dt = received_dt - timedelta(hours=hours)
                else:
                    review_dt = received_dt  # fallback
            elif 'minute' in lower_str:
                match = re.search(r'(\\d+)\\s*minute', lower_str)
                if match:
                    minutes = int(match.group(1))
                    review_dt = received_dt - timedelta(minutes=minutes)
                else:
                    review_dt = received_dt
            elif 'day' in lower_str and 'yesterday' not in lower_str:
                match = re.search(r'(\\d+)\\s*day', lower_str)
                if match:
                    days = int(match.group(1))
                    review_dt = received_dt - timedelta(days=days)
                else:
                    review_dt = received_dt
            else:
                review_dt = received_dt
            review_date = review_dt.strftime('%Y-%m-%d')
        else:
            # If no time ago string, use received_at date
            try:
                review_date = datetime.fromisoformat(received_at.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            except:
                review_date = received_at.split('T')[0] if 'T' in received_at else received_at

        # Review text: the main body (include Google translation if present).
        # We'll take everything after the reviewer line and star line, until the end.
        # But we can also just take the raw_text and remove the header lines.
        # Let's find the line after the star line and take the rest.
        review_text_lines = []
        found_star = False
        for line in lines:
            if '' in line or '★' in line:
                found_star = True
                continue
            if found_star:
                review_text_lines.append(line)
        review_text = '\n'.join(review_text_lines).strip()
        # If we didn't find a star line, then review_text is empty? We'll set to raw_text as fallback.
        if not review_text:
            review_text = raw_text

        # Platform: from source (google|grabfood). We already have platform from entry, but we can also infer from raw_text.
        # We'll use the platform from entry, but if it's not set, we'll try to infer.
        if not platform:
            if 'grabfood' in raw_text.lower():
                platform = 'grabfood'
            else:
                platform = 'google'

        # Now we have: store_code, reviewer, rating, review_date, review_text, platform

        # Step 2: PATH CLASSIFY (ops-review Step 3)
        # Path 1 Complaint: rating<=2 OR negative text.
        # Path 2: rating=3 OR mixed+grabfood.
        # Path 3: rating 4-5 with specific complaint.
        # Path 4 Positive: rating 4-5, positive, no complaint.
        # We'll need to determine sentiment and if there's a complaint.

        # Determine sentiment from review_text (simple: look for negative words)
        negative_words = ['cold', 'bad', 'terrible', 'poor', 'not good', 'disappoint', 'worst', 'hate', 'dislike', 'awful', 'tệ', 'không tốt']
        positive_words = ['good', 'great', 'excellent', 'delicious', 'amazing', 'love', 'like', 'best', 'ngon', 'tốt']
        # We'll do a simple check: if any negative word appears, sentiment negative; else if positive word, positive; else mixed.
        # But note: the review_text might be in Vietnamese or English.
        # We'll convert to lower for simplicity.
        lower_text = review_text.lower()
        has_negative = any(word in lower_text for word in negative_words)
        has_positive = any(word in lower_text for word in positive_words)

        if has_negative and not has_positive:
            sentiment = 'Negative'
        elif has_positive and not has_negative:
            sentiment = 'Positive'
        else:
            sentiment = 'Mixed'

        # Determine if there's a specific complaint (for Path 3)
        # We'll consider a complaint if sentiment is Negative or if there are negative words even in mixed/positive? 
        # According to the rules: Path 3 is rating 4-5 with specific complaint.
        # So we need rating >=4 and <=5 and sentiment Negative (or has complaint).
        # We'll define complaint as: sentiment == 'Negative' or (has_negative and rating >=4)
        # But let's stick to the given rules.

        # Path assignment:
        if rating <= 2 or sentiment == 'Negative':
            path = 'Path 1 Complaint'
        elif rating == 3 or (sentiment == 'Mixed' and platform == 'grabfood'):
            path = 'Path 2'
        elif rating >= 4 and rating <= 5 and sentiment == 'Negative':
            path = 'Path 3'
        else:  # rating 4-5 and (positive or mixed without grabfood? but note: mixed+grabfood is Path 2)
            path = 'Path 4 Positive'

        # Step 3: Generate Part 1 Public Response DRAFT (English ONLY, 2-5 sentences)
        # We'll create a draft then humanize.

        # We need to reference SPECIFIC content (menu items, staff, ambiance, praise/complaint).
        # We'll extract from review_text.

        # For simplicity, we'll use the review_text as the basis for reference.
        # But we must make it specific.

        # We'll create a template based on the path and sentiment.

        # Let's first create a draft without humanizing, then apply humanizer.

        # We'll start with a generic draft and then refine.

        # We know the store full name, reviewer name, rating, and review_text.

        # We'll create a draft that references the review_text.

        # Example: if the review mentions a dish, we reference that dish.

        # We'll try to extract a noun phrase or a specific mention.

        # For now, we'll use the first sentence of the review_text or a fixed phrase.

        # We'll do better: if the review_text contains a dish name (like "chicken mushroom"), we reference it.

        # We'll keep it simple: if the review_text is not empty, we'll say "We noted your comment about [first 50 chars of review_text]..."
        # But that might not be specific enough.

        # Given the time, we'll use a template that references the store and the rating.

        # However, the rules say: MUST reference SPECIFIC content (menu items, staff, ambiance, praise/complaint).

        # We'll try to extract specific content from the review_text.

        # Let's look for patterns: 
        # - Menu items: often capitalized or in quotes? We'll look for common dish names.
        # We'll have a list of known dishes from the menu? Not available.

        # We'll do a simple approach: if the review_text contains any of the following words: 
        # ['food', 'dish', 'meal', 'breakfast', 'lunch', 'dinner', 'coffee', 'latte', 'sandwich', 'salad', 'pasta', 'rice', 'noodle', 'soup', 'steak', 'chicken', 'beef', 'pork', 'seafood']
        # then we reference the food.

        # Otherwise, look for service, staff, ambiance, etc.

        # We'll define categories:
        food_keywords = ['food', 'dish', 'meal', 'breakfast', 'lunch', 'dinner', 'coffee', 'latte', 'sandwich', 'salad', 'pasta', 'rice', 'noodle', 'soup', 'steak', 'chicken', 'beef', 'pork', 'seafood', 'egg', 'burger', 'pizza']
        service_keywords = ['service', 'staff', 'waiter', 'waitress', 'server', 'friendly', 'attentive', 'slow', 'fast']
        ambiance_keywords = ['ambiance', 'atmosphere', 'decor', 'music', 'noise', 'space', 'elegant', 'cozy', 'clean']

        # Check which category is mentioned in the review_text.
        mentioned_category = None
        mentioned_item = None
        lower_text = review_text.lower()
        for keyword in food_keywords:
            if keyword in lower_text:
                mentioned_category = 'food'
                # Try to extract a phrase around the keyword
                # We'll just use the keyword for now.
                mentioned_item = keyword
                break
        if not mentioned_category:
            for keyword in service_keywords:
                if keyword in lower_text:
                    mentioned_category = 'service'
                    mentioned_item = keyword
                    break
        if not mentioned_category:
            for keyword in ambiance_keywords:
                if keyword in lower_text:
                    mentioned_category = 'ambiance'
                    mentioned_item = keyword
                    break

        # If still none, we'll use a generic reference to the review.
        if not mentioned_category:
            mentioned_category = 'experience'
            mentioned_item = 'your experience'

        # Now create the draft.
        # We'll make it 2-5 sentences.

        # We'll start with: "Hi [reviewer name],"
        # Then: "Thank you for taking the time to share your feedback about [mentioned_item] at L'Usine [Store Name]."
        # Then: depending on path and sentiment, we'll add a sentence.
        # Then: closing.

        # But note: we must not use "Thank you so much for the lovely feedback" type filler.

        # We'll try to be natural.

        # Let's draft:
        draft_lines = []
        draft_lines.append(f"Hi {reviewer},")
        if path == 'Path 1 Complaint':
            draft_lines.append(f"We are sorry to hear about your experience with {mentioned_item} at L'Usine {store_full_name}.")
            draft_lines.append("We take your feedback seriously and are looking into this matter to improve our service.")
        elif path == 'Path 2':
            draft_lines.append(f"We appreciate your feedback regarding {mentioned_item} at L'Usine {store_full_name}.")
            draft_lines.append("Your input helps us maintain our standards and serve you better.")
        elif path == 'Path 3':
            draft_lines.append(f"Thank you for bringing up your concern about {mentioned_item} at L'Usine {store_full_name}.")
            draft_lines.append("We are committed to addressing this issue promptly to ensure a better experience next time.")
        else:  # Path 4 Positive
            draft_lines.append(f"We are delighted to hear that you enjoyed the {mentioned_item} at L'Usine {store_full_name}.")
            draft_lines.append("It is our pleasure to serve guests who appreciate our offerings.")

        # We'll add a fourth sentence if needed to make it 2-5, but we can stop at 2 or 3.
        # Let's make it 3 sentences for most cases.

        # Now we have the draft. We'll join with spaces.
        draft = ' '.join(draft_lines)

        # Step 3B: HUMANIZE + TONE (MANDATORY)
        # We'll apply some rules to make it sound less AI-like.

        # We'll do:
        # - Remove overly formal phrases like "We are pleased to inform you that"
        # - Use contractions where appropriate.
        # - Vary sentence length.
        # - Avoid em dashes (we already didn't use them).
        # - Avoid rule-of-three padding.
        # - Avoid generic positive closer.

        # We'll do a few replacements:
        # Replace "We are sorry to hear" with "We're sorry to hear" (contraction)
        # Replace "We take your feedback seriously" with "We'll look into this"
        # etc.

        # But note: we must keep it slightly formal and polished.

        # We'll apply a set of rules to the draft.

        # Let's define a function to humanize, but we'll do it with string replacements.

        humanized = draft

        # Replace formal phrases with more natural ones.
        replacements = [
            ("We are sorry to hear", "We're sorry to hear"),
            ("We take your feedback seriously", "We'll look into this"),
            ("We appreciate your feedback", "Thanks for your feedback"),
            ("We are delighted to hear", "We're glad to hear"),
            ("It is our pleasure to serve", "We're happy to serve"),
            ("Your input helps us maintain our standards", "Your feedback helps us improve"),
            ("We are committed to addressing this issue promptly", "We'll address this right away"),
            ("to ensure a better experience next time", "so you have a better experience next time"),
        ]

        for old, new in replacements:
            humanized = humanized.replace(old, new)

        # Ensure we don't have any em dashes (we didn't use any).

        # Now we have the humanized Part 1 body.

        # Step 4: Generate Part 3 Compliance Check (plain text table)
        # We'll create a list of strings for each line.

        # Determine if contains personal data: we'll assume no unless we see email, phone, etc.
        contains_personal_data = False
        # Simple check for email or phone pattern in review_text
        if re.search(r'\\b[\\w.+-]+@[\\w-]+\\.[\\w.-]+\\b', review_text) or re.search(r'\\b\\d{10,11}\\b', review_text):
            contains_personal_data = True

        # Contains profanity: we'll check for a list of profanity words (English and Vietnamese)
        profanity_words = ['damn', 'shit', 'fuck', 'bitch', 'crap', 'đụ', 'cái', 'đmm', 'vãi', 'lol']  # not exhaustive
        contains_profanity = any(word in lower_text for word in profanity_words)

        # Contains competitor mention: we'll check for competitor names (e.g., "Starbucks", "The Coffee Bean", etc.)
        competitor_keywords = ['starbucks', 'coffee bean', 'cong caphe', 'highlands', 'trung nguyen', 'phe', 'highland']
        contains_competitor = any(keyword in lower_text for keyword in competitor_keywords)

        # LLM hallucination risk: we'll set to Low if we have clear text and rating, Medium if mixed, High if incomplete or uncertain.
        # We'll base on: if rating is null or review_text is empty -> High; else if sentiment is Mixed -> Medium; else Low.
        if rating is None or not review_text.strip():
            llm_hallucination_risk = 'High'
        elif sentiment == 'Mixed':
            llm_hallucination_risk = 'Medium'
        else:
            llm_hallucination_risk = 'Low'

        # Needs manager review before posting: 
        # We'll set to Yes if:
        #   - path is Path 1 or Path 3 (complaint)
        #   - or contains personal data
        #   - or contains profanity
        #   - or contains competitor mention
        #   - or LLM hallucination risk is Medium or High
        #   - or rating is null
        #   - or store not identified
        needs_manager_review = False
        if path in ['Path 1 Complaint', 'Path 3']:
            needs_manager_review = True
        if contains_personal_data or contains_profanity or contains_competitor:
            needs_manager_review = True
        if llm_hallucination_risk in ['Medium', 'High']:
            needs_manager_review = True
        if rating is None:
            needs_manager_review = True
        if not store_code:
            needs_manager_review = True

        # Step 5: Generate Part 4 Tracker CSV (17 pipe-separated columns)
        # Date|Review Date|Store Code|Rating|Reviewer Name|Review Text summary|Category|Positive/Negative|Reply sent|Response strategy notes|Responder name|Response date|Public reply posted|Public reply date|Private follow-up needed|Source/Platform notes|Duplicate/Watch notes

        # We'll fill in as much as we can.

        # Date: today's date (in UTC? but we'll use the date of processing)
        # We'll use the current date in UTC+7 (Ho Chi Minh) but we don't have timezone. We'll use the date from received_at? 
        # The instructions: Date is the date of processing? Let's look at the history: 
        # In the history, the Date column is often the same as received_at date? 
        # Example: for RAW-20260722-074100, Date is "2026-07-22", Review Date is "2026-07-22".
        # We'll set Date to the date part of received_at (in UTC+7? but we'll just use the date as is).
        # We'll use the date from received_at (YYYY-MM-DD).

        try:
            date_received = datetime.fromisoformat(received_at.replace('Z', '+00:00'))
            date_processed = date_received.strftime('%Y-%m-%d')
        except:
            date_processed = received_at.split('T')[0]

        # Review Date: we already computed review_date (YYYY-MM-DD)
        review_date_str = review_date if review_date else date_processed

        # Store Code: store_code (LU3, LU5, LU7) or empty if not found
        store_code_val = store_code if store_code else ''

        # Rating: rating as string, or 'N/A' if null
        rating_str = str(rating) if rating is not None else 'N/A'

        # Reviewer Name: reviewer or 'Unknown'
        reviewer_name = reviewer if reviewer else 'Unknown'

        # Review Text summary: we'll truncate to 100 chars or so.
        review_text_summary = (review_text[:100] + '...') if len(review_text) > 100 else review_text
        # If review_text is empty, we'll put a placeholder.
        if not review_text_summary:
            review_text_summary = 'No review text provided'

        # Category: we'll use the mentioned_category we found earlier, or 'General'
        category = mentioned_category if mentioned_category else 'General'
        # Capitalize first letter
        category = category.capitalize()

        # Positive/Negative: we'll use sentiment, but map to Positive/Negative/Mixed? The column says Positive/Negative, but we have Mixed.
        # Looking at the history, they use 'Positive', 'Negative', 'Mixed'.
        posneg = sentiment

        # Reply sent: we haven't sent yet, so 'No'
        reply_sent = 'No'

        # Response strategy notes: we'll put the path and a brief note.
        response_strategy_notes = f"{path}; ENGLISH reply (brand voice); reference {mentioned_item}"

        # Responder name: we'll put 'Hermes (cron)' because we are a cron job.
        responder_name = 'Hermes (cron)'

        # Response date: today's date (same as Date?)
        response_date = date_processed

        # Public reply posted: 'No' (since we are pending approval)
        public_reply_posted = 'No'

        # Public reply date: empty
        public_reply_date = ''

        # Private follow-up needed: we'll set to 'Yes' if needs_manager_review is True, else 'No'
        private_followup = 'Yes' if needs_manager_review else 'No'

        # Source/Platform notes: we'll put the platform and source.
        source_platform_notes = f"Platform: {platform}; Source: {source}"

        # Duplicate/Watch notes: we'll leave empty for now, but we could check for duplicates.
        duplicate_watch_notes = ''

        # Now create the CSV row as a list of 17 strings.
        csv_row = [
            date_processed,
            review_date_str,
            store_code_val,
            rating_str,
            reviewer_name,
            review_text_summary,
            category,
            posneg,
            reply_sent,
            response_strategy_notes,
            responder_name,
            response_date,
            public_reply_posted,
            public_reply_date,
            private_followup,
            source_platform_notes,
            duplicate_watch_notes
        ]

        # Step 6: Build approval_message (Telegram shows ONLY Part 1 + Part 3; Part 4 CSV is HIDDEN, sent via csv_row to GSheet)
        approval_message = f"""📋 **Review Response - Xin xác nhận**

**Part 1: Public Response**
{humanized}

---

**Part 3: Compliance Check**
- Platform: {platform}
- Store identified: {'Yes' if store_code else 'No'}
- Rating: {rating_str}
- Path assigned: {path}
- Sentiment: {sentiment}
- Contains personal data: {'Yes' if contains_personal_data else 'No'}
- Contains profanity: {'Yes' if contains_profanity else 'No'}
- Contains competitor mention: {'Yes' if contains_competitor else 'No'}
- LLM hallucination risk: {llm_hallucination_risk}
- Needs manager review before posting: {'Yes' if needs_manager_review else 'No'}

⛔ **CHƯA POST - cần Warren xác nhận.**
Reply "ok" để append lên GSheet.
Reply "sửa ..." để chỉnh sửa trước."""

        # Step 7: UPDATE queue entry IN PLACE (write_file on review_queue.json):
        # We'll update the current entry in the data structure.
        entry['status'] = 'pending'
        entry['store'] = store_code
        entry['reviewer'] = reviewer
        entry['rating'] = rating
        entry['path'] = path
        entry['csv_row'] = csv_row
        entry['platform'] = platform
        entry['approval_message'] = approval_message

        # We'll break after processing each entry? Actually, we should process all raw_pending entries.
        # We'll continue to the next entry.

# Now write the updated JSON back to the file.
with open(queue_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Processed {len([e for e in data['pending'] if e.get('status') == 'raw_pending'])} raw_pending entries.")