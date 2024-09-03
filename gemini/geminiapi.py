import os
import google.generativeai as genai

genai.configure(api_key=os.environ["API_KEY"])

# Create the model
generation_config = {
    "temperature": 0.0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
    history=[]
)

information = """
Vita Chiropractic - Chiropractor Services Chiro Newstead
Vita Chiropractic - Chiropractor Services Chiro Newstead
Home
Book Online Now
Services
Chiropractic
Remedial Massage
Myofascial Cupping
Pregnancy Massage
Pricing
Blog
Gift Cards
Privacy policy
Contact
Vita Chiropractic & Massage in Newstead
Welcome to
Vita Chiropractic & Massage
.
Our clinic offers chiropractic and therapeutic, deep tissue massage in the Fortitude Valley / New Farm / Newstead area, conveniently located at 68 Commercial Rd (corner of Masters St and Commercial Rd), Newstead (less than 200 meters from Gasworx).
We specialise in treating pain and offer a personalised service for every client.  If you need help with treatment of a specific injury, want to improve your posture, or need help repairing, stretching and energising your body while training, make an appointment and start feeling better today!
BOOK ONLINE NOW
Treatments available
+ Health rebates available﻿
+ ﻿Chiropractic﻿
+ Remedial Ma﻿ssage﻿﻿﻿
+ Deep Tissue Massage
+
﻿﻿Pre-natal / Pregnancy Massage﻿﻿
+
Trigger Point Therapy
+
﻿Myofascial Cupping﻿
+
prices
start f﻿rom $70
Trading hours
By appointment.  Closing time indicates last appointment end time.
Monday           1pm - 6:30pm
Tuesday           CLOSED
Wednesday     8:30am – 6:30pm
Thursday         8:30am - 6:30pm
Friday               CLOSED
Saturday          CLOSED
BOOK ONLINE NOW
What is chiropractic?
Chiropractic is a healthcare discipline that focuses on the diagnosis and treatment of mechanical disorders of the musculoskeletal system, particularly the spine. Chiropractors primarily use their hands to perform manual adjustments and manipulations to the spine or other parts of the body. The goal of chiropractic care is to alleviate pain, improve function, and promote the body's natural ability to heal itself without the use of medication or surgery.
Chiropractors believe that proper alignment of the body's musculoskeletal structure, particularly the spine, allows the body to heal itself. They use various techniques, including spinal adjustments, manipulation, and other manual therapies to address issues related to the body's alignment, joint mobility, and overall musculoskeletal function.
Chiropractic services are commonly sought for conditions such as back pain, neck pain, headaches, and musculoskeletal issues. Chiropractors may also provide advice on exercise, ergonomics, and lifestyle changes to complement their treatments.
Benefits of chiropractic care
Chiropractors have an in-depth understanding of the human body, the central nervous system and all
of
its functions.
By focusing on your entire body, including all your muscles, joints
, nerves
and the musculoskeletal system
,
chiropractor services are able to treat a number of different conditions.
Below are some of the
benefits
you’ll
receive
from treatment at Vita Chiropractic
:
+ Decreased
pain in one or two sessions
+ Headache relief
+ Increased range of motion
+ Relie
f of
chronic pain
+ Focus on the root cause of your pain
BOOK ONLINE NOW
Issues we work with
Chiropractic treatments can be used to manage a wide range of conditions such as:
+ Headaches & migraines
+ Lower back pain
+ Sciatica
+ Neck & shoulder pain
+ Postural issues
+ Tendonitis pain
+ Tennis elbow
& Golfer's elbow
+ Muscular injuries
+ Sporting injuries
+ Joint pain
+TMJ adjustment
+ Surgery prevention
Why choose us?
At
Vita
Chiropractic, our
main focus
is you.
We treat a wide range of symptoms in people of all ages, from children to the elderly, providing you with the most effective chiropractic treatment to relieve your pain.
We
will use
our
knowledge and experience to ensure you understand your condition and to support you through the treatment process
.
Our aim is to
help manage your transition to healing and living your best life.
+ Convenient
location in Newstead
+ Treatments tailored for your unique needs
+ Holistic treatment for your pain
Areas we serve:
Located in Newstead, an inner northern river suburb of Brisbane, we are a few minutes away from the following suburbs:
+
New Farm
+
Fortitude Valley
+
Spring Hill
+
Bowen Hill
+
Herston (Royal Brisbane and Women's Hospital)
+
Albion
+
Windsor
+ Hamilton
+ Paddington
BOOK ONLINE NOW
Special offer
Buy 10 massage treatments and get one free.
* Offers are transferable
Gift vouchers
Massage gift vouchers available at the clinic or we can post them to you or someone special.
BOOK ONLINE NOW
Vita Chiropractic & Massage
68 Commercial Rd    Newstead     QLD     4006
Phone / Text 0408 828 838
Home
Book Online Now
Services
Chiropractic
Remedial Massage
Myofascial Cupping
Pregnancy Massage
Pricing
Blog
Gift Cards
Privacy policy
Contact 
"""

def safe_send_message(query):
    try:
        response = chat_session.send_message(query)
        return response.text
    except genai.types.generation_types.StopCandidateException as e:
        print(f"Response stopped due to safety concerns: {e}")
        return "n/a"

response1 = safe_send_message(f"""
    Summarize the following content and extract the address, contact number, and name:
    {information}
    Please respond with only address.
    If any information is missing or unclear, leave it as 'n/a'.
""")

response2 = safe_send_message(f"""
    Summarize the following content and extract the contact number:
    {information}
    Please respond with only contact number.
    If any information is missing or unclear, leave it as 'n/a'.
""")

response3 = safe_send_message(f"""
    Summarize the following content and extract the name:
    {information}
    Please respond with only name.
    If any information is missing or unclear, leave it as 'n/a'.
""")

response4 = safe_send_message(f"""
    Summarize the following content and extract the about:
    {information}
    Please respond with only about.
    If any information is missing or unclear, leave it as 'n/a'.
""")

print(response1)
print(response2)
print(response3)
print(response4)