# Limitless OS - Example Conversations

**Sample conversation flows demonstrating agent behavior and expected outcomes**

---

## Table of Contents

1. [Conversation 1: Ideal Path (Qualified → Warm Pitch → Immediate Close)](#conversation-1-ideal-path)
2. [Conversation 2: With Objection (Qualified → Warm Pitch → Price Objection → Close)](#conversation-2-with-objection)
3. [Conversation 3: Not Qualified (Wrong Niche → Nurture)](#conversation-3-not-qualified)
4. [Conversation 4: Multi-Session Resume (Session 1 + Session 2)](#conversation-4-multi-session-resume)

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

## Conversation 3: Not Qualified
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

## Conversation 4: Multi-Session Resume
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
