from xml.etree.ElementInclude import include
import query2

import mysql.connector
from datetime import date, datetime, timedelta

# connect to the database
DB = mysql.connector.connect(
  host="localhost",
  user="root", #hostname
  password="Satwik@78", #password
  database="mystore"
)
cursor = DB.cursor()

# function to create a new customer record
def create_customer():
    print("Please enter your details:")
    customer_name = input("Name: ")
    email = input("Email: ")
    passcode = input("Password: ")
    address = input("Address: ")
    phone = int(input("Phone number: "))
    dob = input("Date of birth (YYYY-MM-DD): ")
    age =int(input("Age: "))
    gender = input("Gender: ")
    
    
    cursor.execute("INSERT INTO customer (customer_name, email, passcode, address, contact_number,date_of_birth, age, gender) VALUES (%s, %s, %s, %s, %s, %s,%s,%s)", (customer_name, email, passcode, address, phone, dob, age , gender))
    DB.commit()
    
    print("Customer created successfully!")

# function to check login credentials and return customer ID
def login():
    print("Please enter your login details:")
    email = input("Email: ")
    passcode = input("Password: ")
    
    cursor.execute("SELECT customer_id FROM customer WHERE email = %s AND passcode = %s", (email, passcode))
    result = cursor.fetchall()
    
    if result:
        print("Login successful!")
        return result[0]
    else:
        print("Invalid email or password.")
        return None
    
def login1():
    print("Please enter your login details:")
    admin_name = input("Email: ")
    passcode = input("Password: ")
    
    cursor.execute("SELECT admin_id FROM admin WHERE admin_name = %s AND passcode = %s", (admin_name, passcode))
    result = cursor.fetchall()
    
    if result:
        print("Login successful!")
        return result[0]
    else:
        print("Invalid email or password.")
        return None
    
def login3():
    print("Please enter your login details:")
    supplier_name = input("supplier_name: ")
    supplier_contact = input("supplier_contact: ")
    
    cursor.execute("SELECT supplier_id FROM wholesale_supplier WHERE supplier_name = %s AND supplier_contact = %s", (supplier_name, supplier_contact))
    result = cursor.fetchall()
    
    if result:
        print("Login successful!")
        return result[0]
    else:
        print("Invalid email or password.")
        return None

# function to display the product list
def show_products():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    
    print("Available products:")
    print("ID | Name | mfg_company |date-of-mfg | type | price | quantity| net_weight | size | colour | brand ")
    for product in products:
        print(product[0], "|", product[1], "|", product[2], "|", product[3], "|",  product[4],"|" , product[5],"|", product[6],"|", product[7],"|" ,product[8],"|" ,product[9],"|" ,product[10], )


def add_to_cart():
    result=login()
    customer_id=result[0]
    
    # ask for the product ID and quantity
    product_id = input("Enter the ID of the product you want to add to your cart: ")
    quantity = int(input("Enter the quantity: "))
    # check if the product is available and the quantity is valid
    cursor.execute("SELECT quantity FROM products WHERE product_id=%s", (product_id,))
    product_stock = cursor.fetchone()[0]
    if product_stock < int(quantity):
        print("Sorry, the product is out of stock.")
        return
    # add the product to the cart
    cursor.execute("INSERT INTO cart (customer_id, product_id, quantity) VALUES (%s, %s, %s)", (customer_id, product_id, quantity))
    DB.commit()
    print("Item added to cart.")
    
def view_cart():
    # get the customer ID from the login details
    result=login()
    customer_id=result[0]
    # show the contents of the cart
    cursor.execute("SELECT products.product_name, products.price, cart.quantity FROM cart INNER JOIN products ON cart.product_id = products.product_id WHERE cart.customer_id = %s", (customer_id,))
    cart_items = cursor.fetchall()
    if len(cart_items) == 0:
        print("Your cart is empty")
    else:
        total = 0
        print("Cart contents:")
        print("Name | Price | Quantity")
        for item in cart_items:
            print(item[0], "|", item[1], "|", item[2])
            total += item[1] * item[2]
        print("Total: $" + str(total))
    
    
def place_order():
    # ask for customer's login credentials
    result=login()
    customer_id=result[0]
    # show the customer's cart
    cursor.execute("SELECT cart.cart_id, products.product_name, products.price, cart.quantity FROM cart JOIN products ON cart.product_id = products.product_id WHERE cart.customer_id = %s", (customer_id,))
    cart_items = cursor.fetchall()
    if not cart_items:
        print("Your cart is empty.")
        return
    print("Your cart:")
    print("ID | Name | Price | Quantity")
    total = 0
    for item in cart_items:
        print(item[0], "|", item[1], "|", item[2], "|", item[3])
        total += item[2] * item[3]
    print("Total:", total)
    # ask for confirmation
    confirm = input("Do you want to place the order? (y/n) ")
    if confirm.lower() != "y":
        return
    # get the current date and delivery date
    current_date = datetime.now().strftime('%Y-%m-%d')
    delivery_date = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
    # create the order
    cursor.execute("INSERT INTO orders (customer_id, order_date, delivery_date, total) VALUES (%s, %s, %s, %s)", (customer_id, current_date, delivery_date, total))
    order_id = cursor.lastrowid
    # empty the cart
    cursor.execute("DELETE FROM cart WHERE customer_id = %s", (customer_id,))
    DB.commit()
    print("Order placed successfully!")
    print("Order ID:", order_id)
    print("Order date:", current_date)
    print("delivery date:", delivery_date)
    
def do_payment():
    result=login()
    customer_id=result[0]
    print("Choose a payment method:")
    print("1. UPI")
    print("2. Online Banking")
    print("3. NEFT")
    print("4. COD")
    method = input("Enter your choice: ")
    if method == "1":
        upi_id = input("Enter your UPI ID: ")
        amount = input("Enter the amount: ")
        print(f"Transferring {amount} to {upi_id} via UPI...")
        # perform the UPI transaction here
        cursor.execute("INSERT INTO payment ( amount, payment_type,customer_id) VALUES (%s, %s, %s)", ( amount, "UPI",customer_id))
        DB.commit()
        print("Payment successful!")
    elif method == "2":
        bank_name = input("Enter your bank name: ")
        account_number = input("Enter your account number: ")
        amount = input("Enter the amount: ")
        print(f"Transferring {amount} to {bank_name} account {account_number} via online banking...")
        # perform the online banking transaction here
        if include:
            print("Generating invoice...")
            # include the payment in the customer's payments
            cursor.execute("INSERT INTO payment ( amount, payment_type,customer_id) VALUES ( %s, %s, %s)", ( amount, "Online Banking",customer_id))
            DB.commit()
        print("Payment successful!")
    elif method == "3":
        neft_id = input("Enter the NEFT ID: ")
        amount = input("Enter the amount: ")
        print(f"Transferring {amount} to {neft_id} via NEFT...")
        # perform the NEFT transaction here
        cursor.execute("INSERT INTO payment ( amount, payment_type,customer_id) VALUES ( %s, %s, %s)", ( amount, "NEFT",customer_id))
        DB.commit()
        print("Payment successful!")
    elif method == "4":
        print("Paying cash on delivery...")
        # perform the COD payment here
        if include:
            print("Generating invoice...")
            # include the payment in the customer's payments
            cursor.execute("INSERT INTO payment ( amount, payment_type,customer_id) VALUES ( %s, %s, %s)", ( amount, "COD",customer_id))
            DB.commit()
        print("Payment successful!")
    else:
        print("Invalid choice.")


def update_product(): 

# get user input for the new value
    new_value = int(input("Enter the new value: "))

# get user input for the record to be updated
    record_id = int(input("Enter the ID of the record to be updated: "))

# execute the update statement
    update_query = "UPDATE products SET quantity = %s WHERE product_id = %s"
    values = (new_value, record_id)
    cursor.execute(update_query, values)

# commit the changes to the database
DB.commit()

# print a message to confirm the update
print(cursor.rowcount, "record(s) updated")
    
    
    

# main function
def main():
    
    print('choose user type\n')
    print('1.customer \n2.admin \n3.supplier \n4.exit')
    t=int(input('enter user type: '))
    if(t==1): #customer
        g= True
        while(g):
            print('Hello customer! \n')
            print("Welcome to the Online Retail Store!")
            print("1. Create new customer account")
            print("2. Login as existing customer")
            choice = input("Enter your choice: ")
            if choice == "1":
                    create_customer()
                    login()
            elif choice == "2":
                    customer_id = login()
                    if customer_id:
                        print('Hello customer! \n')
                        print('1.list of products \n \
                   2.products of  size=S \n \
                   3.products of  size=M \n \
                   4.products of  size=L\n \
                   5.products of  size=XS \n \
                   6.products of  size=XL \n \
                   7.all accesosier \n \
                   8.all clothes \n ')
            a=int(input('choose functionality: '))
            if(a==1): 
                show_products()
                
            elif(a==2):
                query2.list_filter5()
                
            elif(a==3):
                query2.list_filter6()
                
            elif(a==4):
                query2.list_filter8()
                
            elif(a==5):
                query2.list_filter2()
            elif(a==6):
                query2.list_filter7()
            elif(a==7):
                query2.list_filter3()
                
            elif(a==8):
                query2.list_filter4()

            else:
                break
            add_to_cart()

            view_cart()

            place_order()

            do_payment()
        
    elif (t==2): #admin
        h=True
        while(h):
            admin_id=login1()
            if admin_id:
                print('Hello admin! \n')
                print('1.list of products \n \
                2.details of payment and customer \n \
                3.order details \n \
                4.wholesale_suppler details \n \
                5.supply_details \n \
                6.list of managers \n \
                7. list of couriers guys \n \
                8. payment details \n \
                9.exit \n ')
                b=int(input('choose functionality: '))
                if (b==1): 
                    show_products()
            
                elif (b==2):
                    query2.List_Prod()
            
                elif (b==3):
                    query2.orders()
            
                elif(b==4): 
                    query2.wholesale_supplier()
                
                elif(b==5):
                    query2.supply_details()
                
                elif(b==6):
                    query2.manager()
                
                elif(b==7):
                    query2.courier()
            
        
                elif(b==8):
                    query2.payment()
                    
                else:
                    break   
                
    
    elif (t==3): #supplier
        k=True
        while(k):
            supplier_id=login3()
            if supplier_id:
                print('1.products to be re-supplied \n \
                       2.update_products \n')
                c=int(input('Enter query number: '))
                if (c==1): 
                    query2.refilled()
                elif (c==2):
                    update_product()
                else:
                    break
        
            
    elif(t==4): #exit
        f=False



# call the main function
main()


cursor.close()
DB.close()