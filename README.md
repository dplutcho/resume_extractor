===============================================
ResumeExtract
===============================================

What is ResumeExtract?
--------------

ResumeExtract is a service for extracting key information from resumes. At early stage of 
development, only keywords and entities can be extracted. In the future ResumeExtract 
may include methods for extracting facts a summary, and identifying similar/related resumes. 

Limitations and development path
--------------

The two bigest limitations of ResumeExtract, which are next in the development 
queue, are that extraction can only occur for my resume and only in text format. 
The plan is to add a URI parameter allowing the ResumeExtract user/consumer to 
point to any Resume and for ResumeExtract to extract text from that source. 

Python libraries utilized
--------------

ResumeExtract depends on the topia (a keyword extraction library), OpenCalais (an 
entity extraction web-service) and its python client called 'Calais', along with NLTK 
(The Natural Language Toolkit) ResumeExtract also utilizes the restlite python package 
along with the wsgiref python package. 

Service utilization
--------------
To utilize the ResumeExtrac service, go to
    http://ec2-50-17-167-145.compute-1.amazonaws.com:8000

This url will return all of the available methods, which can be appended to the 
base url above.

Note that the /resume_text/ method is a convenience to allow users to see the 
extracted text utilized during the information extraction process. Currently this 
is a text version of my resume. 

Further information
--------------

Contact darin.plutchok@gmail.com