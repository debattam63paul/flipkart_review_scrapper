from flask import Flask, request, render_template
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
import csv
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app= Flask(__name__)

@app.route('/', methods = ['GET'])
@cross_origin()    # For accessing the function from anywhere globally, from any country
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")  # replacing space with non-space
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            flipkart_page = requests.get(flipkart_url)    # No need to close this connection, it will autometically close
            flipkart_html = bs(flipkart_page.content, 'html.parser')

            bigbox = flipkart_html.find_all('div', {'class':'_1AtVbE col-12-12'})
            del bigbox[0:3]
            global review
            review=[]
            # Fetching the product links
            for i in range(5):
                productLink = 'https://www.flipkart.com' + bigbox[i].div.div.div.a['href']
                product_request = requests.get(productLink)
                product_html = bs(product_request.content, 'html.parser')

                comment_box = product_html.find_all('div', {'class': '_16PBlm'}) 

                # Fetching all the comments one by one as a dictionary and storing all the dictionaries in reviews list

                for j in range(3):
                    try:
                        Product = searchString
                    except:
                        Product = 'No product name'
                        logging.info('name')

                    try:
                        ProductName = bigbox[i].div.div.find_all('a', {'class': 's1Q9rs'})[0].text
                    except:
                        ProductName = 'No product name'
                        logging.info('ProductName')

                    try:
                        Price = bigbox[i].div.div.div.find_all('div', {'class': '_30jeq3'})[0].text
                    except:
                        Price = 'No price mentioned'
                        logging.info('Price')


                    try:
                        Name = comment_box[j].div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    except:
                        Name = 'Name not found'
                        logging.info('Name')
            
                    try:
                        Rating = comment_box[j].div.div.div.div.text
                    except:
                        Rating = 'No rating'
                        logging.info('Rating')

                    try:
                        CommentHead = comment_box[j].div.div.div.p.text
                    except:
                        CommentHead = 'No comment heading'
                        logging.info('CommentHead')

                    try:
                        Comment = comment_box[j].div.div.find_all('div', {'class': ''})[0].text
                    except:
                        Comment = 'No comment'
                        logging.info('Comment')
            

                    mydict = {"Product": Product,"ProductName":ProductName,"Price":Price, "Name": Name, "Rating": Rating, "CommentHead": CommentHead,"Comment": Comment}
                    review.append(mydict)
            
            logging.info("log my final result {}".format(review))

            
            # storing all the data inside mongodb database
            import pymongo
            client = pymongo.MongoClient('mongodb+srv://debattam63paul:98307948paul@cluster0.ddavie6.mongodb.net/?retryWrites=true&w=majority')
            db = client['flipcart_scrapper']
            collection = db['scrapper_flipcart']
            collection.insert_many(review)
            client.close()   # Always dont forget to close the connection
            
            return render_template('result.html', review=review)
          
        
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
        
        
        
    else:
        print('Only post method is allowed')
        return render_template('index.html')



if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)

# Note that here we can see the url in the scrapper.log file

# To install the packages, first write the packages inside requirements.txt, then in terminal
# write pip install -r requirements.txt





