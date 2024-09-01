from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return sentiment.polarity, sentiment.subjectivity

def interpret_sentiment(polarity, subjectivity):
    if polarity <= -0.5:
        polarity_text = "The brief has a very negative tone, which might not be engaging. A negative tone can demotivate your audience and reduce the effectiveness of your messaging. Consider revising the content to include more positive and inspiring language."
    elif polarity < -0.1:
        polarity_text = "The brief has a somewhat negative tone. While it's important to address challenges, ensure that the overall message remains optimistic and solution-oriented to keep your audience engaged."
    elif polarity <= 0.1:
        polarity_text = "The brief has a neutral tone. This is balanced but may lack emotional impact. Consider adding elements that evoke positive emotions to make your message more compelling."
    elif polarity <= 0.5:
        polarity_text = "The brief has a positive tone, which is generally engaging. Positive language can inspire and motivate your audience, making your campaign more effective."
    else:
        polarity_text = "The brief has a very positive tone, which is highly engaging. A positive tone can significantly boost audience morale and drive better engagement and action."

    if subjectivity <= 0.3:
        subjectivity_text = "The brief is very objective, focusing on facts. While factual information is crucial, consider incorporating some subjective elements like testimonials or personal stories to connect emotionally with your audience."
    elif subjectivity <= 0.5:
        subjectivity_text = "The brief is fairly objective. This balance is good, but adding a bit more personal touch or opinion can make the content more relatable and persuasive."
    elif subjectivity <= 0.7:
        subjectivity_text = "The brief is somewhat subjective, focusing on opinions. While opinions can be powerful, ensure they are backed by facts to maintain credibility and trust."
    else:
        subjectivity_text = "The brief is very subjective, focusing heavily on opinions. High subjectivity can make the content feel biased. Balance it with factual information to strengthen your argument and credibility."

    return polarity_text, subjectivity_text