#MySQL Python Connector
import mysql.connector
from datetime import date, datetime, timedelta

DB = mysql.connector.connect(
  host="localhost",
  user="root", #hostname
  password="Satwik@78", #password
  database="mystore"
)

cursor = DB.cursor()


#xxxxxxxxxxxxxxxxxxxxxxx EMBEDDED FUNCTIONS xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

def List_Prod(): #List details of all Products of a certain Category
    
    query = "select payment.payment_id, payment.amount,customer.customer_name \
from payment \
join customer on payment.customer_id=customer.customer_id;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")

def supplies():
    query = "select supply_details.supplier_id, supply_details.total_amount,supply_details.Quantity,wholesale_supplier.supplier_id \
from supply_details \
join wholesale_supplier on supply_details.supplier_id=wholesale_supplier.supplier_id;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def membership():
    query = "select membership_status.membership_type, customer.customer_id \
from membership_status \
join customer on membership_status.customer_id=customer.customer_id;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def list_products():
    query = "select distinct * \
from products;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def list_filter1():
    query = "select distinct * \
from filters \
where size>45;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")   
    
def list_filter2():
    query = "select distinct * \
from products \
where size='XS';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 
    
def list_filter5():
    query = "select distinct * \
from products \
where size='S';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 
    
def list_filter6():
    query = "select distinct * \
from products \
where size='M';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 

def list_filter7():
    query = "select distinct * \
from products \
where size='XL';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")     
 
def list_filter8():
    query = "select distinct * \
from products \
where size='L';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 
    
     
def list_filter3():
    query = "select distinct * \
from products \
where product_type='accesories';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def list_filter4():
    query = "select distinct * \
from products \
where product_type='clothes';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def refilled():
    query = "select distinct * \
from products \
where quantity<5;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")  
 
def customer_details():
    query = "select distinct * \
from customer; "
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")      
  
def wholesale_supplier():
    query = "select distinct * \
from wholesale_supplier; "
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")  
    
def orders():
    query = "select distinct * \
from orders;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 
    
def supply_details():
    query = "select distinct * \
from supply_details;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 
    
def manager():
    query = "select distinct * \
from employee \
where employee_type='manager';"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 
    
def courier():
    query = "select distinct * \
from employee \
where employee_type ='courier'"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")

def payment():
    query = "select distinct * \
from payment;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n") 

def drilldown():
    query = "select customer_id, customer_name, avg(age) as A \
from customer \
group by customer_id, customer_name\
with rollup \
having customer_id is not null and customer_name is not null;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def rollup():
    query = "select payment_id, customer_id,sum(amount) as S \
from payment \
group by payment_id,customer_id \
with rollup;"
    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def dice():
    query = "select product_name, product_type,colour,brand, sum(price) as p \
from products \
where product_type='clothes' and colour='blue' \
group by product_name,product_type,colour,brand;"

    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
    
def pivot():
    query = "select employee_id, employee_name, \
sum( case when employee_type='manager' and employee_age > 40 then salary else 0 end) as m, \
sum( case when employee_type='courier' and employee_age > 40 then salary else 0 end) as c \
from employee \
group by employee_id, employee_name;"

    cursor.execute(query)
    result = cursor.fetchall()
    for x in result:
        print(x)
    print("\n")
       
        


#Ending
#cursor.close()
#DB.close()