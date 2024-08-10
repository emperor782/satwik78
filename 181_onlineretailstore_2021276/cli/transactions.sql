-- Transaction 1 (customer1 updates her profile)
start TRANSACTION;
-- Update customer1's profile information
UPDATE customer
 SET email = 'alice@example.com', contact_number = 9844221675 
 WHERE customer_id= 3;
select * from customer where customer_name='Amble Stear';
-- Commit the transaction
COMMIT;

-- Transaction 2 (customer2 updates his profile)
start TRANSACTION;
-- Update customer2's profile information
UPDATE customer SET email = 'doe@example.com', contact_number = 4567890345 WHERE customer_id = 4;
select * from customer where customer_name ='Doe Aitkenhead';
-- Commit the transaction
COMMIT;


start transaction;
update products set quantity=quantity -4 
where product_id=5;
commit;

start transaction;
update products set quantity=quantity-5
where product_id=5;
commit;