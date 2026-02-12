import re
from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional

class FAQMatcher:
    """Simple NLP-based FAQ matcher using keyword matching and text similarity"""
    
    def __init__(self):
        self.faqs = self._load_faqs()
        
    def _load_faqs(self) -> List[Dict[str, any]]:
        """Load FAQ database with categories and keywords"""
        return [
            # Greetings & Basic Interactions
            {
                "id": 1,
                "category": "greeting",
                "question": "Hello / Hi / Greetings",
                "answer": "Hello! Welcome to Batna University Chatbot. I'm here to help you with any questions about:\n- Course registration and enrollment\n- Tuition fees and payments\n- Academic information and grades\n- Campus facilities and services\n- Exams and schedules\n- Student services\n\nHow can I assist you today?",
                "keywords": ["hello", "hi", "hey", "greetings", "salut", "bonjour", "salam", "مرحبا", "السلام عليكم"],
                "variants": ["hello", "hi there", "hey", "good morning", "good afternoon", "bonjour", "salut", "مرحبا", "السلام عليكم"]
            },
            {
                "id": 2,
                "category": "greeting",
                "question": "How are you?",
                "answer": "I'm functioning well, thank you for asking! I'm here and ready to help you with any questions about Batna University. What would you like to know?",
                "keywords": ["how are you", "comment allez-vous", "ça va", "كيف حالك", "كيفك"],
                "variants": ["how are you", "how are you doing", "comment vas-tu", "comment allez-vous", "كيف حالك"]
            },
            {
                "id": 3,
                "category": "greeting",
                "question": "Thank you / Thanks",
                "answer": "You're very welcome! I'm glad I could help. If you have any other questions about Batna University, feel free to ask anytime. Have a great day!",
                "keywords": ["thank", "thanks", "merci", "شكرا", "شكراً"],
                "variants": ["thank you", "thanks", "thank you very much", "merci", "merci beaucoup", "شكرا", "شكراً جزيلاً"]
            },
            {
                "id": 4,
                "category": "greeting",
                "question": "Goodbye / See you",
                "answer": "Goodbye! It was nice helping you today. Feel free to come back anytime you have questions about Batna University. Take care!",
                "keywords": ["goodbye", "bye", "see you", "au revoir", "مع السلامة", "وداعا"],
                "variants": ["goodbye", "bye", "see you later", "au revoir", "à bientôt", "مع السلامة", "وداعاً"]
            },
            {
                "id": 5,
                "category": "help",
                "question": "What can you help me with?",
                "answer": "I can help you with many aspects of Batna University, including:\n\n📚 **Academic:**\n- Course registration and schedules\n- Grading system and checking grades\n- Attendance policies\n\n💰 **Financial:**\n- Tuition fees and payment methods\n- Scholarships and financial aid\n\n🏢 **Campus Life:**\n- Campus facilities (library, gym, cafeteria)\n- Library hours and services\n- Student housing\n\n📝 **Student Services:**\n- Getting student ID cards\n- Email and portal access\n- Administrative procedures\n\n📅 **Important Dates:**\n- Registration deadlines\n- Exam periods\n- Academic calendar\n\nJust ask me anything!",
                "keywords": ["help", "what can you do", "aide", "مساعدة", "ماذا تفعل"],
                "variants": ["what can you help with", "what do you do", "how can you help", "aide", "مساعدة"]
            },
            
            # Registration & Enrollment
            {
                "id": 6,
                "category": "registration",
                "question": "How do I register for courses?",
                "answer": "**Course Registration Process:**\n\n1. Log into your student portal at portal.univ-batna2.dz\n2. Navigate to 'Course Registration' section\n3. Select your desired courses from the available list\n4. Verify your selections and check for time conflicts\n5. Submit your registration\n6. Pay the registration fees within the deadline\n\n**Important Notes:**\n- Registration opens 2 weeks before each semester\n- Make sure you meet course prerequisites\n- Limited seats - register early!\n- Late registration incurs additional fees\n\n**Need Help?** Visit the Registrar's Office (Building B, Room 201) or email: registrar@batna2.dz",
                "keywords": ["register", "registration", "enroll", "enrollment", "course", "signup", "sign up", "inscription", "تسجيل"],
                "variants": ["how to register", "registration process", "enroll in courses", "course enrollment", "comment s'inscrire", "كيف أسجل"]
            },
            {
                "id": 7,
                "category": "registration",
                "question": "What are the registration deadlines?",
                "answer": "**Registration Deadlines 2024-2025:**\n\n🍂 **Fall Semester:**\n- Early Registration: August 15 - September 10\n- Regular Registration: Until September 15\n- Late Registration: September 16-20 (with late fee)\n\n🌸 **Spring Semester:**\n- Early Registration: January 15 - February 10\n- Regular Registration: Until February 15\n- Late Registration: February 16-20 (with late fee)\n\n☀️ **Summer Session:**\n- Registration: May 15 - June 10\n- Late Registration: June 11-15 (with late fee)\n\n**Late Fee:** 5,000 DZD\n\n⚠️ **Important:** No registration accepted after late period ends!",
                "keywords": ["deadline", "last day", "registration date", "when", "due date", "date limite", "موعد", "آخر موعد"],
                "variants": ["registration deadline", "when to register", "registration dates", "date limite d'inscription", "موعد التسجيل"]
            },
            {
                "id": 8,
                "category": "registration",
                "question": "Can I drop a course after registration?",
                "answer": "**Course Drop Policy:**\n\n✅ **Weeks 1-2 (Add/Drop Period):**\n- Full refund (100%)\n- No record on transcript\n- No academic penalty\n\n⚠️ **Weeks 3-6 (Withdrawal Period):**\n- Partial refund (50%)\n- 'W' (Withdrawal) appears on transcript\n- Does not affect GPA\n\n❌ **After Week 6:**\n- No refund\n- 'WF' (Withdrawal Fail) on transcript\n- Counts as failed course (affects GPA)\n\n**How to Drop:**\n1. Submit drop form via student portal, OR\n2. Visit Registrar's Office with student ID\n3. Confirmation email sent within 24 hours\n\n**Questions?** Contact: registrar@batna2.dz",
                "keywords": ["drop", "withdraw", "remove course", "cancel registration", "annuler", "حذف المادة", "الانسحاب"],
                "variants": ["drop a course", "withdraw from course", "cancel course", "annuler un cours", "حذف مادة"]
            },
            
            # Tuition & Fees
            {
                "id": 9,
                "category": "tuition",
                "question": "How much are the tuition fees?",
                "answer": "**Tuition Fees (Per Semester):**\n\n🎓 **Undergraduate Programs:**\n- Base Tuition: 50,000 DZD\n- Lab Fees (if applicable): 5,000 DZD\n\n🎓 **Master's Programs:**\n- Base Tuition: 75,000 DZD\n- Research Fees: 10,000 DZD\n\n🎓 **PhD Programs:**\n- Base Tuition: 100,000 DZD\n- Research & Lab Access: 15,000 DZD\n\n**Additional Fees:**\n- Registration Fee: 5,000 DZD (one-time per year)\n- Library Access: 2,000 DZD\n- Sports Facilities: 1,500 DZD\n- Student Services: 1,000 DZD\n- Late Payment Fee: 3,000 DZD\n\n**Payment Deadline:** Within 2 weeks of registration\n\n💡 **Scholarships Available** - Ask about financial aid options!",
                "keywords": ["tuition", "fees", "cost", "price", "payment", "how much", "money", "frais", "رسوم", "المصاريف"],
                "variants": ["tuition fees", "how much does it cost", "university fees", "payment", "frais de scolarité", "كم الرسوم"]
            },
            {
                "id": 10,
                "category": "tuition",
                "question": "What payment methods are accepted?",
                "answer": "**Accepted Payment Methods:**\n\n🏦 **Bank Transfer:**\n- Bank: BNA (Banque Nationale d'Algérie)\n- Account: 00799999123456789\n- Reference: Your Student ID\n\n💵 **Cash Payment:**\n- Visit: Finance Office (Building A, Room 105)\n- Hours: 8:00 AM - 4:00 PM (Sunday-Thursday)\n- Bring: Student ID + Payment receipt\n\n📮 **CCP (Compte Courant Postal):**\n- CCP Number: 1234567-89 Batna\n- Reference: Student ID + Semester\n\n💳 **Online Payment:**\n- Portal: portal.univ-batna2.dz/payment\n- Accepted: CIB, EDAHABIA, Visa, Mastercard\n- Instant confirmation\n\n📧 **Proof Required:** Email payment receipt to finance@batna2.dz\n\n**Questions?** Finance Office: +213 33 123 460",
                "keywords": ["payment", "pay", "method", "transfer", "cash", "online", "credit card", "paiement", "طريقة الدفع"],
                "variants": ["how to pay", "payment methods", "paying tuition", "modes de paiement", "كيف أدفع"]
            },
            
            # Academic Information
            {
                "id": 11,
                "category": "academic",
                "question": "What is the grading system?",
                "answer": "**Batna University Grading Scale:**\n\n📊 **Algerian System (0-20):**\n- **16-20:** Excellent (Très Bien) - A\n- **14-15.99:** Very Good (Bien) - B\n- **12-13.99:** Good (Assez Bien) - C\n- **10-11.99:** Satisfactory (Passable) - D\n- **0-9.99:** Fail (Ajourné) - F\n\n**Minimum Passing Grade:** 10/20\n\n🌍 **International GPA Conversion:**\n- 16-20 → 4.0 GPA\n- 14-15.99 → 3.0-3.99 GPA\n- 12-13.99 → 2.0-2.99 GPA\n- 10-11.99 → 1.0-1.99 GPA\n- Below 10 → 0.0 GPA\n\n**Grade Components:**\n- Midterm Exam: 30%\n- Final Exam: 50%\n- Assignments/Projects: 15%\n- Attendance/Participation: 5%\n\n**Grade Appeals:** Within 5 days of grade posting",
                "keywords": ["grade", "grading", "marks", "score", "gpa", "evaluation", "notation", "درجات", "تقييم"],
                "variants": ["grading system", "how grades work", "grade scale", "système de notation", "نظام التقييم"]
            },
            {
                "id": 12,
                "category": "academic",
                "question": "How can I access my grades?",
                "answer": "**Accessing Your Grades:**\n\n💻 **Online (Recommended):**\n1. Go to portal.univ-batna2.dz\n2. Log in with your credentials\n3. Click 'Academic Records'\n4. Select 'View Grades'\n5. Choose semester/year\n6. Download transcript (PDF available)\n\n📱 **Mobile App:**\n- Download 'Batna University' app\n- Same login credentials\n- Instant notifications when grades posted\n\n📧 **Email Notification:**\n- Automatic email when grades available\n- Check your university email regularly\n\n🏢 **In Person:**\n- Visit: Registrar's Office\n- Bring: Student ID\n- Request: Official transcript\n- Fee: 500 DZD (official sealed copy)\n\n⏰ **Grade Posting Timeline:**\n- Posted within 2 weeks after final exams\n- Midterm grades: 1 week after exam\n\n**Trouble Accessing?** IT Support: itsupport@batna2.dz",
                "keywords": ["access grades", "view grades", "check grades", "see results", "transcript", "consulter notes", "الاطلاع على النتائج"],
                "variants": ["how to see grades", "check my grades", "view results", "voir mes notes", "كيف أرى درجاتي"]
            },
            {
                "id": 13,
                "category": "academic",
                "question": "What is the attendance policy?",
                "answer": "**Attendance Policy:**\n\n✅ **Required Attendance:** 75% minimum\n\n📋 **Absence Limits:**\n- 3 absences allowed per course (no questions asked)\n- 4th absence: Warning letter sent\n- 5th absence: Grade reduction (-10%)\n- Each additional absence: -10% from final grade\n- More than 25% absence (7+ classes): **Automatic Failure**\n\n🏥 **Excused Absences:**\n- Medical reasons (with certificate)\n- Family emergency (with documentation)\n- University-approved activities\n- Submit within **3 days** of absence\n\n📝 **Documentation Required:**\n- Medical certificate from approved doctor\n- Official letter for emergencies\n- Email to professor AND registrar@batna2.dz\n\n⏰ **Tardiness:**\n- 3 late arrivals (>15 min) = 1 absence\n- Leaving early = 1 absence\n\n**Attendance Tracking:** Electronic system via student ID card scan\n\n**Questions?** Contact your instructor or studentaffairs@batna2.dz",
                "keywords": ["attendance", "absence", "present", "miss class", "skip", "assiduité", "présence", "الحضور", "الغياب"],
                "variants": ["attendance policy", "attendance requirements", "missing class", "politique de présence", "سياسة الحضور"]
            },
            
            # Campus Life
            {
                "id": 14,
                "category": "campus",
                "question": "What facilities are available on campus?",
                "answer": "**Campus Facilities at Batna University:**\n\n📚 **Central Library:**\n- 5 floors, 500+ study seats\n- 50,000+ books, journals, e-resources\n- Quiet study rooms & group study areas\n- Free WiFi & printing services\n- Hours: 8 AM - 8 PM (extended during exams)\n\n💻 **Computer Labs:**\n- 5 labs with 200+ computers\n- Latest software for all majors\n- High-speed internet\n- Technical support available\n- Open: 8 AM - 6 PM\n\n🏃 **Sports Complex:**\n- Indoor gym with modern equipment\n- Football field (grass)\n- Basketball courts (2)\n- Volleyball court\n- Tennis courts (2)\n- Changing rooms & showers\n\n🍽️ **Student Cafeteria:**\n- Subsidized meals\n- Breakfast: 50 DZD\n- Lunch: 100 DZD\n- Snacks & beverages\n- Hours: 7 AM - 5 PM\n\n🙏 **Prayer Rooms:**\n- Separate rooms for men & women\n- Available in all buildings\n\n📖 **Study Rooms:**\n- Group study rooms (booking required)\n- Silent study areas\n- 24/7 access during exam periods\n\n🏥 **Medical Clinic:**\n- First aid & basic healthcare\n- Nurse on duty 8 AM - 4 PM\n- Emergency contact: +213 33 123 470\n\n🖨️ **Printing Center:**\n- Building C, Ground Floor\n- Black & white: 5 DZD/page\n- Color: 20 DZD/page\n- Binding services available\n\n🚗 **Parking:**\n- Student parking (free with ID)\n- Visitor parking (paid)\n- Bicycle racks\n\n**Campus Map:** Available at reception or online portal",
                "keywords": ["facilities", "campus", "library", "gym", "cafeteria", "sports", "amenities", "équipements", "مرافق"],
                "variants": ["campus facilities", "what's on campus", "university facilities", "installations du campus", "مرافق الجامعة"]
            },
            {
                "id": 15,
                "category": "campus",
                "question": "What are the library hours?",
                "answer": "**Central Library Hours:**\n\n📅 **Regular Semester:**\n- **Sunday-Thursday:** 8:00 AM - 8:00 PM\n- **Friday:** 8:00 AM - 12:00 PM, 2:00 PM - 6:00 PM (Closed 12-2 PM for Friday prayer)\n- **Saturday:** 8:00 AM - 2:00 PM\n\n📚 **Exam Period (Extended Hours):**\n- **Sunday-Thursday:** 7:00 AM - 10:00 PM\n- **Friday:** 8:00 AM - 10:00 PM\n- **Saturday:** 7:00 AM - 10:00 PM\n\n🎉 **Holidays:**\n- Closed on national holidays\n- Reduced hours during Ramadan\n- Check calendar on library website\n\n💻 **Digital Library:**\n- 24/7 online access to e-resources\n- Access via portal.univ-batna2.dz/library\n\n📱 **Contact:**\n- Phone: +213 33 123 465\n- Email: library@batna2.dz\n- WhatsApp: +213 555 123 456\n\n**Services:**\n- Book borrowing (3 weeks, 5 books max)\n- Study room reservations\n- Research assistance\n- Printing & scanning\n- Computer access",
                "keywords": ["library", "hours", "time", "open", "close", "schedule", "horaires", "bibliothèque", "ساعات المكتبة"],
                "variants": ["library hours", "when is library open", "library schedule", "horaires de la bibliothèque", "أوقات المكتبة"]
            },
            
            # Student Services
            {
                "id": 16,
                "category": "services",
                "question": "How do I get a student ID card?",
                "answer": "**Student ID Card Application:**\n\n📋 **Required Documents:**\n1. Passport-size photo (recent, white background)\n2. Registration confirmation (from portal)\n3. National ID card or passport (original + copy)\n4. Payment receipt (1,000 DZD)\n\n🏢 **Application Process:**\n1. Visit: Student Services Office (Building B, Room 110)\n2. Submit documents\n3. Pay 1,000 DZD fee at cashier\n4. Photo will be taken on-site\n5. Fill out application form\n6. Receive collection receipt\n\n⏰ **Processing Time:** 3-5 business days\n\n🎫 **Card Collection:**\n- Same office (Student Services)\n- Bring: Collection receipt + National ID\n- Office hours: 8 AM - 4 PM (Sunday-Thursday)\n\n💳 **Card Features:**\n- Photo identification\n- Barcode for library access\n- Building access control\n- Exam hall entry\n- Cafeteria discount\n\n🔄 **Lost/Damaged Card:**\n- Report immediately: studentservices@batna2.dz\n- Replacement fee: 2,000 DZD\n- Processing: 5-7 days\n\n⚠️ **Important:** Student ID required for:\n- Exams (no ID = no entry!)\n- Library access\n- Campus facility use\n- Discounts & services",
                "keywords": ["student id", "card", "identification", "badge", "carte étudiant", "بطاقة الطالب"],
                "variants": ["get student card", "student id card", "university card", "obtenir carte étudiant", "الحصول على بطاقة الطالب"]
            },
            {
                "id": 17,
                "category": "services",
                "question": "Is there student housing available?",
                "answer": "**Student Housing (Résidence Universitaire):**\n\n🏠 **Availability:** Yes! On-campus dormitories available\n\n📋 **Priority Given To:**\n1. International students\n2. Students from distant regions (>100 km)\n3. Scholarship recipients\n4. Students with financial need\n\n💰 **Monthly Rent:**\n- **Shared Room** (2-3 students): 8,000 DZD/month\n- **Shared Room** (4 students): 6,000 DZD/month\n- **Single Room** (limited): 15,000 DZD/month\n\n🛏️ **Room Features:**\n- Bed, desk, wardrobe per student\n- Shared bathroom facilities\n- WiFi included\n- 24/7 security\n- Common kitchen areas\n\n⏰ **Application Period:**\n- **Fall Semester:** May 1 - July 30\n- **Spring Semester:** November 1 - December 30\n\n📝 **How to Apply:**\n1. Log into student portal\n2. Go to 'Housing Application'\n3. Fill out application form\n4. Upload required documents:\n   - ID copy\n   - Registration proof\n   - Distance certificate (if applicable)\n   - Income statement (for financial aid)\n5. Submit and wait for confirmation\n\n✅ **Results:** Announced 2 weeks before semester starts\n\n📧 **Contact:**\n- Email: housing@batna2.dz\n- Phone: +213 33 123 468\n- Office: Student Services Building\n\n**Note:** Space is limited - apply early!",
                "keywords": ["housing", "dormitory", "residence", "accommodation", "room", "dorm", "logement", "résidence", "السكن الجامعي"],
                "variants": ["student housing", "dormitories", "place to stay", "résidence universitaire", "السكن الجامعي"]
            },
            
            # Scholarships & Financial Aid
            {
                "id": 18,
                "category": "financial_aid",
                "question": "What scholarships are available?",
                "answer": "**Scholarship Opportunities:**\n\n🏆 **Merit Scholarships:**\n- **Requirement:** GPA ≥ 15/20\n- **Benefit:** 50% tuition reduction\n- **Renewable:** Every semester (maintain GPA)\n- **Deadline:** June 1st annually\n\n💰 **Need-Based Financial Aid:**\n- **Requirement:** Family income documentation\n- **Benefit:** 25%-100% tuition coverage\n- **Includes:** Possible monthly stipend (10,000-20,000 DZD)\n- **Application:** Through Financial Aid Office\n\n🔬 **Research Scholarships (Master's/PhD):**\n- **Benefit:**\n  - Full tuition waiver\n  - Monthly stipend: 25,000 DZD (Master's), 35,000 DZD (PhD)\n  - Research funding\n  - Conference travel support\n- **Requirement:** Research proposal approval\n\n⚽ **Sports Scholarships:**\n- **For:** University team members\n- **Benefit:** 25% tuition reduction + training support\n- **Requirement:** Active team participation\n\n🌍 **International Student Scholarships:**\n- **Available for:** Non-Algerian students\n- **Benefit:** Tuition waiver + housing support\n- **Limited spots:** Contact international office\n\n📝 **Application Process:**\n1. Complete online application\n2. Submit supporting documents:\n   - Academic transcripts\n   - Income statements (for need-based)\n   - Recommendation letters\n   - Personal statement\n3. Interview (if required)\n4. Results: July 15th\n\n📧 **Contact:**\n- Financial Aid Office\n- Email: financialaid@batna2.dz\n- Phone: +213 33 123 462\n- Office: Building A, Room 115\n\n**Don't wait - apply early! Limited funding available.**",
                "keywords": ["scholarship", "financial aid", "funding", "grant", "support", "bourse", "aide financière", "منحة"],
                "variants": ["scholarships available", "financial help", "scholarship opportunities", "bourses disponibles", "المنح الدراسية"]
            },
            
            # Technical Support
            {
                "id": 19,
                "category": "technical",
                "question": "I forgot my student portal password. How do I reset it?",
                "answer": "**Password Reset Instructions:**\n\n💻 **Online Self-Reset:**\n1. Go to portal.univ-batna2.dz\n2. Click 'Forgot Password?'\n3. Enter your student email address\n4. Check your email for reset link (check spam folder!)\n5. Click the link (valid for 24 hours)\n6. Create new password:\n   - Minimum 8 characters\n   - Include: uppercase, lowercase, number, symbol\n7. Log in with new password\n\n📧 **Didn't Receive Email?**\n- Wait 5-10 minutes\n- Check spam/junk folder\n- Verify email address is correct\n- Try again\n\n🏢 **In-Person Reset:**\nIf online reset fails:\n1. Visit: IT Support Office\n2. Location: Building A, Room 102\n3. Bring: Student ID + National ID\n4. Office hours: 8 AM - 4 PM (Sunday-Thursday)\n5. Password reset on the spot\n\n📱 **Contact IT Support:**\n- Email: itsupport@batna2.dz\n- Phone: +213 33 123 475\n- WhatsApp: +213 555 123 789\n\n🔐 **Password Tips:**\n- Don't share your password\n- Change it every 3 months\n- Use unique password (not same as email/social media)\n- Write it down securely if needed\n\n⚠️ **Security Notice:**\n- University will NEVER ask for your password via email\n- Don't click suspicious links\n- Log out after using public computers",
                "keywords": ["password", "reset", "forgot", "login", "access", "portal", "mot de passe", "كلمة السر", "نسيت"],
                "variants": ["reset password", "forgot password", "can't login", "réinitialiser mot de passe", "نسيت كلمة السر"]
            },
            
            # Exams
            {
                "id": 20,
                "category": "exams",
                "question": "When are the exam periods?",
                "answer": "**Exam Schedule 2024-2025:**\n\n🍂 **Fall Semester:**\n- **Midterm Exams:** November 10-20, 2024\n- **Final Exams:** January 15-30, 2025\n- **Makeup/Resit Exams:** February 10-20, 2025\n\n🌸 **Spring Semester:**\n- **Midterm Exams:** April 5-15, 2025\n- **Final Exams:** June 10-25, 2025\n- **Makeup/Resit Exams:** July 5-15, 2025\n\n☀️ **Summer Session:**\n- **Final Exams:** August 20-30, 2025\n\n📅 **Important Dates:**\n- Exam schedules posted: 3 weeks before exams\n- Check your portal for personalized schedule\n- No schedule conflicts guaranteed if registered on time\n\n📝 **Exam Rules:**\n- Arrive 15 minutes early\n- Bring student ID (mandatory!)\n- No phones/smart watches\n- Only approved calculators\n\n🔔 **Schedule Updates:**\n- Email notifications sent\n- Check portal daily during exam period\n- Bulletin boards in each building\n\n📊 **Results:**\n- Posted within 2 weeks after exams\n- Access via portal → Academic Records → Grades\n\n**Questions?** Academic Affairs: academic@batna2.dz",
                "keywords": ["exam", "test", "final", "schedule", "when", "period", "examen", "date", "امتحان", "الاختبار"],
                "variants": ["exam schedule", "when are exams", "exam dates", "calendrier des examens", "مواعيد الامتحانات"]
            },
            {
                "id": 21,
                "category": "exams",
                "question": "What should I bring to exams?",
                "answer": "**Exam Checklist:**\n\n✅ **REQUIRED (Must Have):**\n1. **Valid Student ID Card**\n   - Without ID = NO ENTRY to exam hall!\n   - Lost ID? Get temporary pass from Registrar\n\n2. **Writing Materials:**\n   - Blue or black pens (no pencils for answers)\n   - Pencils (for drafts/diagrams)\n   - Eraser\n   - Ruler (if needed)\n\n3. **Calculator (if allowed):**\n   - Only non-programmable calculators\n   - Check with instructor if permitted\n   - Scientific calculators OK for math/science\n   - Graphing calculators: instructor approval needed\n\n✅ **RECOMMENDED:**\n- Water bottle (clear, no label)\n- Tissues\n- Extra pens\n- Watch (to track time)\n\n❌ **STRICTLY PROHIBITED:**\n- Mobile phones (must be turned off & in bag)\n- Smart watches / fitness trackers\n- Notes, books, papers (unless open-book exam)\n- Programmable calculators\n- Electronic devices (tablets, laptops)\n- Bags on desk (must be on floor)\n- Food (water only)\n- Headphones/earbuds\n- Communication devices\n\n⏰ **Arrival Time:**\n- Arrive 15 minutes before exam start\n- Late arrival (>15 min) = Entry denied\n\n🎯 **Exam Day Tips:**\n1. Check exam location day before\n2. Get good sleep\n3. Eat breakfast\n4. Use restroom before exam\n5. Bring extra pen (in case one fails)\n\n⚠️ **Violations:**\n- Using prohibited items = Exam invalidated + disciplinary action\n- Academic dishonesty = Serious consequences\n\n**Good luck! 🍀**",
                "keywords": ["exam", "bring", "required", "allowed", "need", "apporter", "examen", "ماذا أحضر", "الامتحان"],
                "variants": ["what to bring to exam", "exam requirements", "quoi apporter à l'examen", "ماذا أحضر للامتحان"]
            },
            
            # Contact Information
            {
                "id": 22,
                "category": "contact",
                "question": "How can I contact the university?",
                "answer": "**Batna University Contact Information:**\n\n📍 **Main Campus:**\nRoute de Biskra, Batna 05000, Algeria\n\n📞 **Main Switchboard:**\n- Phone: +213 (0)33 123 456\n- Fax: +213 (0)33 123 457\n\n🌐 **Website:**\nwww.univ-batna2.dz\n\n📧 **General Inquiries:**\ninfo@batna2.dz\n\n---\n\n**Department Contact Details:**\n\n📚 **Admissions Office:**\n- Email: admissions@batna2.dz\n- Phone: +213 33 123 458\n- Building: A, Room 201\n\n📝 **Registrar's Office:**\n- Email: registrar@batna2.dz\n- Phone: +213 33 123 459\n- Building: B, Room 201\n\n💰 **Finance Office:**\n- Email: finance@batna2.dz\n- Phone: +213 33 123 460\n- Building: A, Room 105\n\n💻 **IT Support:**\n- Email: itsupport@batna2.dz\n- Phone: +213 33 123 475\n- WhatsApp: +213 555 123 789\n- Building: A, Room 102\n\n🎓 **Student Affairs:**\n- Email: studentaffairs@batna2.dz\n- Phone: +213 33 123 461\n- Building: B, Room 110\n\n💳 **Financial Aid:**\n- Email: financialaid@batna2.dz\n- Phone: +213 33 123 462\n- Building: A, Room 115\n\n📚 **Library:**\n- Email: library@batna2.dz\n- Phone: +213 33 123 465\n- WhatsApp: +213 555 123 456\n\n🏠 **Housing Office:**\n- Email: housing@batna2.dz\n- Phone: +213 33 123 468\n\n🌍 **International Office:**\n- Email: international@batna2.dz\n- Phone: +213 33 123 470\n\n---\n\n**Office Hours:**\n- Sunday-Thursday: 8:00 AM - 4:00 PM\n- Friday & Saturday: Closed\n- Ramadan hours: 8:00 AM - 2:00 PM\n\n📱 **Social Media:**\n- Facebook: @UnivBatna2\n- Instagram: @batna_university\n- Twitter: @UnivBatna2\n- YouTube: Batna University Official\n\n🚨 **Emergency Contact:**\n- Campus Security: +213 33 123 400\n- Medical Clinic: +213 33 123 470\n- Fire/Emergency: 14 (national)\n\n**We're here to help! 🤝**",
                "keywords": ["contact", "phone", "email", "reach", "call", "address", "contacter", "coordonnées", "تواصل", "رقم"],
                "variants": ["contact university", "phone number", "how to reach", "contacter l'université", "كيف أتواصل"]
            },
        ]
    
    def _preprocess_text(self, text: str) -> str:
        """Normalize and clean text for matching"""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _keyword_match_score(self, query: str, faq: Dict) -> float:
        """Calculate keyword matching score"""
        query_words = set(query.split())
        
        # Check for exact keyword matches in query
        keyword_matches = 0
        for keyword in faq['keywords']:
            keyword_lower = keyword.lower()
            # Check if keyword is in the query as a whole word or substring
            if keyword_lower in query or any(keyword_lower in word for word in query_words):
                keyword_matches += 1
        
        # Bonus for variant matches
        variant_match = any(variant.lower() in query for variant in faq['variants'])
        
        score = keyword_matches / max(len(faq['keywords']), 1)
        if variant_match:
            score += 0.3
        
        return min(score, 1.0)
    
    def _semantic_match_score(self, query: str, faq: Dict) -> float:
        """Calculate semantic similarity score"""
        # Compare with question
        question_similarity = self._calculate_similarity(query, self._preprocess_text(faq['question']))
        
        # Compare with variants
        variant_similarities = [
            self._calculate_similarity(query, self._preprocess_text(variant))
            for variant in faq['variants']
        ]
        max_variant_similarity = max(variant_similarities) if variant_similarities else 0
        
        return max(question_similarity, max_variant_similarity)
    
    def find_best_match(self, user_query: str, threshold: float = 0.3) -> Optional[Dict]:
        """
        Find the best matching FAQ for a user query
        
        Args:
            user_query: The user's question
            threshold: Minimum confidence score (0-1)
        
        Returns:
            Dictionary with 'faq' and 'confidence' or None if no match
        """
        query = self._preprocess_text(user_query)
        
        best_match = None
        best_score = 0
        
        for faq in self.faqs:
            # Calculate combined score
            keyword_score = self._keyword_match_score(query, faq)
            semantic_score = self._semantic_match_score(query, faq)
            
            # Weighted combination (keywords are more reliable)
            combined_score = (keyword_score * 0.6) + (semantic_score * 0.4)
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = faq
        
        if best_score >= threshold:
            return {
                'faq': best_match,
                'confidence': round(best_score, 2),
                'category': best_match['category']
            }
        
        return None
    
    def find_multiple_matches(self, user_query: str, top_k: int = 3, threshold: float = 0.25) -> List[Dict]:
        """
        Find multiple matching FAQs
        
        Args:
            user_query: The user's question
            top_k: Number of top matches to return
            threshold: Minimum confidence score
        
        Returns:
            List of matching FAQs with confidence scores
        """
        query = self._preprocess_text(user_query)
        
        matches = []
        for faq in self.faqs:
            keyword_score = self._keyword_match_score(query, faq)
            semantic_score = self._semantic_match_score(query, faq)
            combined_score = (keyword_score * 0.6) + (semantic_score * 0.4)
            
            if combined_score >= threshold:
                matches.append({
                    'faq': faq,
                    'confidence': round(combined_score, 2),
                    'category': faq['category']
                })
        
        # Sort by confidence and return top k
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        return matches[:top_k]
    
    def get_faqs_by_category(self, category: str) -> List[Dict]:
        """Get all FAQs in a specific category"""
        return [faq for faq in self.faqs if faq['category'] == category]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all FAQ categories"""
        return list(set(faq['category'] for faq in self.faqs))


# Create singleton instance
faq_matcher = FAQMatcher()


def search_faq(query: str) -> Dict:
    """
    Search for FAQ answer
    
    Args:
        query: User's question
    
    Returns:
        Dictionary with answer or indication that no match was found
    """
    match = faq_matcher.find_best_match(query)
    
    if match:
        return {
            'found': True,
            'answer': match['faq']['answer'],
            'question': match['faq']['question'],
            'confidence': match['confidence'],
            'category': match['category']
        }
    else:
        return {
            'found': False,
            'message': 'No FAQ found for this question. The AI will provide a general answer.'
        }
