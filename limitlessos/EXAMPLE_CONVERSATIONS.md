# Limitless OS - Example Conversations

**Sample conversation flows demonstrating agent behavior and expected outcomes**

---

## Table of Contents

1. [Conversation 1: Ideal Path (Qualified → Warm Pitch → Immediate Close)](#conversation-1-ideal-path)
2. [Conversation 2: With Objection (Qualified → Warm Pitch → Price Objection → Close)](#conversation-2-with-objection)
3. [Conversation 3: Multiple Objections (Qualified → Cold Pitch → Multiple Objections → Follow-up)](#conversation-3-multiple-objections)
4. [Conversation 4: Not Qualified (Wrong Niche → Nurture)](#conversation-4-not-qualified)
5. [Conversation 5: Multi-Session Resume (Session 1 + Session 2)](#conversation-5-multi-session-resume)
6. [Conversation 6: Follow-up Sequence (3-Day Follow-ups → Close)](#conversation-6-follow-up-sequence)

---

## Conversation 1: Ideal Path
**Qualified → Warm Pitch → Immediate Close**

### **Scenario**
- Perfect fit: fitness coach, $5K/month revenue, clear pain point
- Qualification score: 0.85
- Ready to buy immediately

### **Conversation Flow**

**[Session Start: Campaign Code ABC123 validated]**

---

**AI (Greeter):**
> Hey there! Thanks for reaching out. Are you a coach in the health, fitness, wellness, or mindset space?

**Lead:**
> Yes, I'm a fitness coach

*[Tool Called: check_niche_fit → niche_fit: true]*  
*[Tool Called: update_stage → qualification]*

---

**AI (Qualifier - Q1):**
> Awesome! What type of fitness coaching do you offer right now?

**Lead:**
> I do online personal training for busy professionals

*[Tool Called: store_qualification_answer(question_number=1, answer="online personal training", parsed_data={business_type: "fitness coaching"})]*

---

**AI (Qualifier - Q2):**
> Nice. What's your monthly revenue from coaching right now?

**Lead:**
> Around $5K per month

*[Tool Called: store_qualification_answer(question_number=2, parsed_data={monthly_revenue: "$5K"})]*

---

**AI (Qualifier - Q3):**
> Got it. How are you currently getting clients? (DMs, ads, referrals, etc.)?

**Lead:**
> Mostly Instagram DMs and some referrals

*[Tool Called: store_qualification_answer(question_number=3, parsed_data={lead_source: "Instagram DMs, referrals"})]*

---

**AI (Qualifier - Q4):**
> Makes sense. What's your biggest challenge in growing your business right now?

**Lead:**
> Honestly, the tech side is overwhelming. I'm using like 10 different tools and they don't talk to each other. Spending more time on admin than coaching.

*[Tool Called: store_qualification_answer(question_number=4, parsed_data={main_pain_point: "tech overwhelm, tool fragmentation"})]*

---

**AI (Qualifier - Q5):**
> I totally hear that. If we gave you a system that could fix that tech overwhelm in the next 14 days, would you be ready to start right away?

**Lead:**
> Absolutely, yes

*[Tool Called: store_qualification_answer(question_number=5, parsed_data={ready_to_invest: true})]*  
*[Tool Called: calculate_qualification_score → score: 0.85, qualified: true, pitch_type: "warm"]*  
*[Tool Called: update_stage → pitch]*

---

**AI (Pitcher - Warm Pitch):**
> Got it. Based on what you've said, I think Limitless OS would be perfect for you. It replaces 50+ tools, automates your business, and launches your high-converting funnel in just 14 days — so you can focus on coaching, not tech headaches. We build everything for you, no tech skills needed.
>
> You can get started for **$297/month + a $997 funnel build**, or **$497/month with the build included**. Which option works best for you?

*[Tool Called: get_personalized_pitch(pitch_type="warm")]*  
*[Tool Called: mark_pitch_delivered(pitch_type="warm")]*

---

**Lead:**
> The $497/month sounds good. I like the all-in-one option.

*[Tool Called: confirm_plan_choice → plan_chosen: "option2"]*  
*[Tool Called: update_stage → closing]*

---

**AI (Closer):**
> Perfect choice! I'm sending you a secure Stripe payment link now. Once you complete payment, you'll receive an email with next steps for your onboarding call. We'll have your funnel built and ready to launch in 14 days. Welcome to Limitless OS!
>
> [Payment Link: https://checkout.stripe.com/pay/xxx]

*[Tool Called: create_stripe_link(plan="option2")]*  
*[Tool Called: send_payment_link]*  
*[Tool Called: mark_payment_link_sent]*  
*[Tool Called: update_stage → complete]*

---

### **State After Conversation**

```json
{
  "instagram_handle": "@fitcoach_mike",
  "campaign_code": "ABC123",
  "current_stage": "complete",
  "qualified": true,
  "qualification_score": 0.85,
  "business_type": "fitness coaching",
  "monthly_revenue": "$5K",
  "main_pain_point": "tech overwhelm",
  "ready_to_invest": true,
  "pitch_delivered": true,
  "pitch_type": "warm",
  "preferred_plan": "option2",
  "payment_link_sent": true,
  "total_interactions": 9
}
```

---

## Conversation 2: With Objection
**Qualified → Warm Pitch → Price Objection → Close**

### **Scenario**
- Qualified fitness coach
- Raises price objection after pitch
- Objection successfully handled

### **Conversation Flow**

**[... Greeting + Qualification completed (score: 0.75) ...]**

---

**AI (Pitcher - Warm Pitch):**
> Got it. Based on what you've said, I think Limitless OS would be perfect for you. It replaces 50+ tools, automates your business, and launches your high-converting funnel in just 14 days — so you can focus on coaching, not tech headaches. We build everything for you, no tech skills needed.
>
> You can get started for **$297/month + a $997 funnel build**, or **$497/month with the build included**. Which option works best for you?

---

**Lead:**
> I like the sound of it but $497/month seems pretty expensive for me right now

*[Tool Called: identify_objection → objection_type: "price"]*  
*[Tool Called: record_objection(objection_type="price")]*  
*[Tool Called: update_stage → objection]*

---

**AI (Objection Handler):**
> Totally understand. Most of our clients actually save $2,000+ per month by replacing their current tools — so it often pays for itself in month one. You mentioned you're using around 10 tools right now, which are probably costing you $500+ monthly, plus all the time trying to make them work together. Knowing that, would you like to start with the $297/month + $997 build, or $497/month with the build included?

*[Tool Called: search_knowledge_base(query="price objection response")]*  
*[Tool Called: mark_objection_handled(objection_type="price")]*

---

**Lead:**
> You're right, when you put it that way. Let's do the $497 option.

*[Tool Called: confirm_plan_choice → plan_chosen: "option2"]*  
*[Tool Called: update_stage → closing]*

---

**AI (Closer):**
> Perfect! I'm sending you a secure Stripe payment link now. Once you complete payment, you'll receive an email with next steps for your onboarding call. Welcome to Limitless OS!
>
> [Payment Link: https://checkout.stripe.com/pay/xxx]

*[Tool Called: create_stripe_link(plan="option2")]*  
*[Tool Called: send_payment_link]*  
*[Tool Called: update_stage → complete]*

---

### **Key Takeaways**
- ✅ Objection acknowledged, not argued
- ✅ Personalized response using qualification data
- ✅ Re-attempted close after handling objection
- ✅ Successful conversion

---

## Conversation 3: Multiple Objections
**Qualified → Cold Pitch → Multiple Objections → Follow-up**

### **Scenario**
- Moderately qualified (score: 0.6)
- Raises price AND time objections
- Needs follow-up sequence

### **Conversation Flow**

**[... Greeting + Qualification completed (score: 0.6) ...]**

---

**AI (Pitcher - Cold Pitch):**
> You sound exactly like the coaches we help with Limitless OS. It's an all-in-one system that automates your coaching business from lead generation to onboarding — replacing 50+ tools and saving up to $2,500/month in software costs.
>
> In 14 days, you'll have your high-converting funnel built, automations set up, and everything integrated into one platform. No tech skills needed — we do it all for you.
>
> We have two simple options: **$297/month + a $997 one-time funnel build**, or **$497/month with the funnel build included**. Which one do you want to start with?

---

**Lead:**
> This sounds great but I'm already stretched thin. I don't think I have the time to set this up and honestly it's a bit more than I wanted to spend

*[Tool Called: identify_objection → objection_type: "time, price"]*  
*[Tool Called: record_objection(objection_type="time")]*  
*[Tool Called: record_objection(objection_type="price")]*  
*[Tool Called: update_stage → objection]*

---

**AI (Objection Handler):**
> I get both of those concerns. Here's the thing — you don't need time to set it up because we do everything for you. You just show up for onboarding, and within 14 days you have a fully automated business running. It's about saving you time, not taking more of it.
>
> And on the cost side, you're already spending more than this each month on multiple tools that don't talk to each other. Limitless OS replaces all of them and saves you $2,500/month. Can I send you the payment link so we can lock your spot for this month's onboarding?

*[Tool Called: search_knowledge_base(query="time objection")]*  
*[Tool Called: search_knowledge_base(query="price objection")]*  
*[Tool Called: mark_objection_handled(objection_type="time")]*  
*[Tool Called: mark_objection_handled(objection_type="price")]*

---

**Lead:**
> I need to think about it

*[Tool Called: update_stage → followup]*

---

**AI (Follow-up):**
> Of course — this is a big decision. What specifically do you need to think about? Is it the price, timing, or something else? Let me address that for you now.

---

**Lead:**
> I just need a day or two to think it over

---

**AI (Follow-up):**
> No problem. Just so you know, we're filling spots for this month's onboarding. If you want your funnel live by February 15th, we'd need to get started this week. I'll follow up with you in a couple of days.

*[Tool Called: increment_followup_count]*

---

### **State After Conversation**

```json
{
  "current_stage": "followup",
  "qualification_score": 0.6,
  "pitch_delivered": true,
  "pitch_type": "cold",
  "objections_raised": ["time", "price"],
  "objections_handled": ["time", "price"],
  "followup_count": 1,
  "payment_link_sent": false
}
```

**→ System will automatically send Day 3 and Day 5 follow-ups**

---

## Conversation 4: Not Qualified
**Wrong Niche → Nurture**

### **Scenario**
- Lead is not in target niche (e-commerce store owner)
- Politely routed to nurture

### **Conversation Flow**

---

**AI (Greeter):**
> Hey there! Thanks for reaching out. Are you a coach in the health, fitness, wellness, or mindset space?

---

**Lead:**
> No, I run an e-commerce store selling fitness products

*[Tool Called: check_niche_fit → niche_fit: false]*  
*[Tool Called: update_stage → nurture]*

---

**AI (Greeter):**
> Got it! Limitless OS is specifically designed for coaches in health, fitness, and wellness — so it might not be the perfect fit for your e-commerce business. But I appreciate you reaching out! If you know any coaches who could benefit, feel free to send them our way.

---

### **State After Conversation**

```json
{
  "current_stage": "nurture",
  "qualified": false,
  "niche_fit": false,
  "business_type": "e-commerce"
}
```

---

## Conversation 5: Multi-Session Resume
**Session 1 (Day 1) + Session 2 (Day 3) - Resume After 2 Days**

### **Scenario**
- Lead starts qualification, answers 2 questions, then disappears
- Returns 2 days later
- System resumes exactly where they left off

---

### **Session 1: Monday, 2:00 PM**

**[Campaign Code ABC123 validated, new lead]**

---

**AI (Greeter):**
> Hey there! Thanks for reaching out. Are you a coach in the health, fitness, wellness, or mindset space?

---

**Lead:**
> Yes, wellness coach

---

**AI (Qualifier - Q1):**
> Awesome! What type of wellness coaching do you offer right now?

---

**Lead:**
> I work with entrepreneurs on stress management and burnout prevention

*[State Saved: business_type="wellness coaching", questions_asked=1]*

---

**AI (Qualifier - Q2):**
> Nice. What's your monthly revenue from coaching right now?

---

**Lead:**
> About $7K

*[State Saved: monthly_revenue="$7K", questions_asked=2]*

---

**[Lead doesn't respond, session ends]**

---

### **Session 2: Wednesday, 6:30 PM (48 hours later)**

**[Lead returns to same URL, Campaign Code ABC123 validated]**  
**[System loads state from database]**

---

**AI (Qualifier - Q3):**
> Welcome back! Let's continue where we left off. How are you currently getting clients? (DMs, ads, referrals, etc.)?

*[System detected: questions_asked=2, so skip to Q3]*

---

**Lead:**
> Mostly through my email list and webinars

*[State Saved: lead_source="email, webinars", questions_asked=3]*

---

**AI (Qualifier - Q4):**
> Got it. What's your biggest challenge in growing your business right now?

---

**Lead:**
> I'm spending way too much time on admin tasks. My systems are all over the place.

*[State Saved: main_pain_point="admin overload", questions_asked=4]*

---

**AI (Qualifier - Q5):**
> I hear you. If we gave you a system that could automate all that admin work in the next 14 days, would you be ready to start right away?

---

**Lead:**
> Yes definitely

*[Tool Called: calculate_qualification_score → score: 0.8]*  
*[Transition to pitch]*

---

### **Key Takeaways**
- ✅ System persisted state across 2-day gap
- ✅ Resumed at exact question where lead left off
- ✅ No questions repeated
- ✅ Seamless experience for lead

---

## Conversation 6: Follow-up Sequence
**3-Day Follow-up Sequence → Close**

### **Scenario**
- Lead pitched, but said "need to think about it"
- Receives 3 follow-ups over 5 days
- Converts on Day 5 follow-up

---

### **Day 1: Initial Pitch**

**[... Qualification + Pitch delivered ...]**

---

**Lead:**
> I need to think about it

*[State: followup_count=0, last_message_at="2025-01-15T14:00:00Z"]*

---

### **Day 2: First Follow-up (24 hours later)**

**[System automatically triggers followup_agent]**

---

**AI (Follow-up Agent):**
> Hey! Just checking in — want to make sure you saw my last message about Limitless OS. This could have you fully automated in 14 days. Any questions I can answer?

*[Tool Called: send_followup_message(followup_number=1, urgency_level="none")]*  
*[Tool Called: increment_followup_count → followup_count=1]*

---

**[No response]**

---

### **Day 4: Second Follow-up (72 hours after initial)**

---

**AI (Follow-up Agent):**
> We're filling spots for this month's onboarding. If you want to launch your funnel by February 15th, we should get you locked in now. Which plan works best for you — $297 + $997 build, or $497/month?

*[Tool Called: send_followup_message(followup_number=2, urgency_level="soft")]*  
*[Tool Called: increment_followup_count → followup_count=2]*

---

**[No response]**

---

### **Day 6: Final Follow-up (120 hours after initial)**

---

**AI (Follow-up Agent):**
> Last call for this month's onboarding spots — we're almost full. If you want to lock in your spot, I can send your link now.

*[Tool Called: send_followup_message(followup_number=3, urgency_level="strong")]*  
*[Tool Called: increment_followup_count → followup_count=3]*

---

**Lead:**
> Okay, let's do it. I'll take the $497 option.

*[Tool Called: confirm_plan_choice → plan_chosen="option2"]*  
*[Tool Called: update_stage → closing]*

---

**AI (Closer):**
> Awesome! I'm so glad you're ready. I'm sending you a secure Stripe payment link now. Welcome to Limitless OS!
>
> [Payment Link: https://checkout.stripe.com/pay/xxx]

*[Tool Called: create_stripe_link(plan="option2")]*  
*[Tool Called: send_payment_link]*  
*[Tool Called: update_stage → complete]*

---

### **Key Takeaways**
- ✅ 3 follow-ups over 5 days (not spammy)
- ✅ Increasing urgency with each follow-up
- ✅ System tracked followup_count automatically
- ✅ Successful conversion on Day 6

---

## Expected Behavior Patterns

### **Agent Response Times**
- **Greeting**: Immediate (no thinking required)
- **Qualification Questions**: 1-2 seconds (simple storage)
- **Pitch Generation**: 2-3 seconds (RAG search)
- **Objection Handling**: 2-3 seconds (RAG search)
- **Payment Link**: 3-4 seconds (Stripe API call)

### **Message Length Guidelines**
- **Greeting**: 1-2 sentences
- **Qualification Questions**: 1 question, no fluff
- **Pitch**: 3-4 sentences max
- **Objection Response**: 2-3 sentences
- **Closing**: 2 sentences + link

### **Tone Examples**

**✅ Good (Conversational)**
> "Got it. Based on what you've said, I think Limitless OS would be perfect for you."

**❌ Bad (Robotic)**
> "Thank you for providing that information. I have analyzed your responses and determined that you are a qualified prospect."

### **Personalization Examples**

**✅ Good (Uses State Data)**
> "You mentioned you're spending too much time on admin. Limitless OS can cut that by 20 hours/week."

**❌ Bad (Generic)**
> "Our system will help you save time."

---

## State Persistence Examples

### **State After Greeting**
```json
{
  "current_stage": "qualification",
  "niche_fit": true,
  "questions_asked": 0
}
```

### **State After Qualification**
```json
{
  "current_stage": "pitch",
  "qualified": true,
  "qualification_score": 0.8,
  "business_type": "fitness coaching",
  "monthly_revenue": "$7K",
  "questions_asked": 5
}
```

### **State After Pitch**
```json
{
  "current_stage": "closing",
  "pitch_delivered": true,
  "pitch_type": "warm"
}
```

### **State After Payment Link Sent**
```json
{
  "current_stage": "complete",
  "payment_link_sent": true,
  "preferred_plan": "option2"
}
```

---

**These examples demonstrate the expected behavior for all agent interactions and serve as a reference for testing and quality assurance.**
