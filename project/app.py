from flask import Flask, render_template,url_for, request, redirect
import psycopg2
# from config import config
from psycopg2 import sql
from psycopg2._psycopg import AsIs
from send_email import send_mail

app = Flask(__name__)

warehouse_id =0

# app.config['MYSQL_HOST']=''
# app.config['MYSQL_USER']=''
# app.config['MYSQL_PASSWORD']=''
# app.config['MYSQL_DB']=''

# mysql = MySQL(app)
# conn = psycopg2.connect("host= localhost dbname = test user=postgres password=Santoshy1")
conn = psycopg2.connect("postgres://fkzyohsugtczzh:f72e8cffd1edbb1a3be4a331af4f69d10496bdd303c8e13b36bb534e13e19980@ec2-3-231-16-122.compute-1.amazonaws.com:5432/d20m5bk52p5h8r")

@app.route('/feedback/', methods=['GET','POST'])
def feedback():
    if request.method=='POST':
        cur = conn.cursor()
        details = request.form
        name = details['name']
        email = details['email']
        phone = details['phone']
        feedback_for = details['feedback_for']
        feedback = details['feedback']
        cur.execute('insert into feedback(name, email, mobile, feedback_for, feedback) values (%s, %s, %s, %s, %s)', (name, email, phone, feedback_for, feedback))
        conn.commit()
        send_mail(name, email, phone, feedback_for, feedback)
        cur.close()
        return render_template('feedback.html', fill = True)
    return render_template('feedback.html', fill=False)

@app.route('/signup_type/', methods=['GET','POST'])
def signup_type():
    if request.method=='POST':
        type = request.form
        type1 = type['submit']
        if type1 == 'Warehouse':
            return redirect('/signup_warehouse')
        else:
            return redirect('/signup/')
    else:
        return render_template('signup_type.html')

@app.route('/signup/', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        userDetails = request.form
        name = userDetails['name']
        username = userDetails['username']
        store_name = userDetails['store_name']
        mobile = userDetails['Mobile']
        if len(mobile) != 10:
            return render_template('signup1.html', fail = False, mob_f = True, pass1 =False)
        password = userDetails['password']
        password2 = userDetails['password2']
        if password != password2:
            return render_template('signup1.html', fail = False, mob_f =False, pass1 =True)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users(name, store_name, mobile, password, username) values(%s, %s, %s, %s, %s);",
                        (name, store_name, mobile, password, username))
            conn.commit()
            cur.close()
            return redirect('/login')
        except:
            cur.close()
            return render_template('signup1.html', fail=True, pass1 = False)
    return render_template('signup1.html', fail=False, pass1 = False)

@app.route('/signup_warehouse', methods=['POST', 'GET'])
def signup_warehouse():
    if request.method=='POST':
        details = request.form
        name = details['name']
        enterprise = details['enterprise']
        owner = details['owner']
        mobile = details['mobile']
        print(len(mobile))
        if len(mobile) != 10:
            return render_template('signup_warehouse1.html', fail = False, mob_f=True, pass1=False)
        username = details['username']
        password = details['password']
        password2 = details['password2']
        if password != password2:
            return render_template('signup_warehouse1.html', fail=False, mob_f=False, pass1=True)
        cur = conn.cursor()
        try:
            cur.execute('insert into warehouses(warehouse_name, enterprise, owner_name, mobile, username, password) values(%s, %s, %s, %s, %s, %s);', (name, enterprise, owner, mobile, username, password))
            conn.commit()
            cur.close()
            return redirect(url_for('login'))
        except:
            cur.close()
            return render_template('signup_warehouse1.html', fail = True, pass1 = False)
            # return <script>alert('username already taken')</script>
    return render_template('signup_warehouse1.html', fail = False, pass1 = False)

# @app.route('/users/')
# def users():
#     cur = conn.cursor()
#     resultValue = cur.execute("SELECT * FROM users;")
#     print(resultValue)
#     # if resultValue>0:
#     userDetails = cur.fetchall()
#     return render_template('users.html', userDetails=userDetails)

# @app.route('/', methods=['GET','POST'])
@app.route('/login' ,methods=['GET','POST'])
def login():
    if request.method=='POST':
        # type = request.args.get('user_type')
        details = request.form
        type = details['user_type']
        print(type)
        user1 = details['user_name']
        password1 = details['password']
        cur = conn.cursor()
        if type == 'Warehouse':
            cur.execute("select password from warehouses where username = (%s)", (user1,))
            # print(cur.fetchone())
            if cur.fetchone() != None:
                cur.execute("select password from warehouses where username = (%s)", (user1,))
                temp_pass= cur.fetchone()[0]
                # print(temp_pass)
                if (temp_pass==password1):
                    cur.execute('select warehouse_id from warehouses where username = (%s)', (user1,))
                    id = cur.fetchone()[0]
                    cur.close()
                    return redirect('/warehouse/'+str(id))
                else:
                    cur.close()
                    return render_template('login1.html', wrong=True)
            else:
                cur.close()
                return render_template('login1.html', wrong=True)
        else:
            cur.execute('select password from users where username =(%s)', (user1,))
            if cur.fetchone() !=None:
                cur.execute('select password from users where username =(%s)', (user1,))
                temp_pass = cur.fetchone()[0]
                print(temp_pass)
                if temp_pass==password1:
                    cur.execute("select id from users where username = (%s) and password = (%s)", (user1, password1))
                    id = cur.fetchone()[0]
                    cur.close()
                    return redirect('/selectwarehouse/' + str(id))
                else:
                    cur.close()
                    return render_template('login1.html', wrong=True)
            else:
                cur.close()
                return render_template('login1.html', wrong=True)
    return render_template('login1.html', wrong=False)

@app.route('/forget_password', methods=['POST','GET'])
def forget_password():
    if request.method=='POST':
        cur=conn.cursor()
        details = request.form
        name = details['name']
        username = details['username']
        type = details['type']
        password = details['new_password']
        if type=='warehouse':
            try:
                cur.execute('update warehouses set password =(%s) where username=(%s) and owner_name=(%s)', (password,username,name))
                cur.close()
                return redirect('/login')
            except:
                return render_template('forget_pass.html',wrong=True)
        elif type=='retail':
            try:
                cur.execute('update users set password =(%s) where username=(%s) and name=(%s)', (password,username,name))
                cur.close()
                return redirect('/login')
            except:
                return render_template('forget_pass.html',wrong=True)
    return render_template('forget_pass.html', wrong=False)

itemlist= None

@app.route('/warehouse/<string:user>', methods=['GET','POST'])
def warehouse(user):
    if request.method == 'POST':
        if request.form['submit'] == 'Add':
            cur = conn.cursor()
            listitem = request.form
            item_name = listitem['item_name']
            company = listitem['company']
            user1 = int(user)
            try:
                price = int(listitem['price'])
            except:
                cur.execute('select * from items where warehouse_id = (%s);', (user1,))
                global itemlist
                itemlist = cur.fetchall()
                cur.close()
                return render_template('warehouse1.html', itemlist=itemlist, price_f=True)
            # print(type(price))
            expiry_date = listitem['expiry_date']
            # print(listitem['availability'])
            availibility =listitem['availability']
            # cur = conn.cursor()
            # user1 = int(user)
            # cur.execute('select * from items where warehouse_id = (%s);', (user1,))
            # global itemlist
            # itemlist=cur.fetchall()
            cur.execute("insert into items(item_name, company, expiry_date, price, availability, warehouse_id) values (%s, %s, %s, %s, %s, %s);",(item_name, company, expiry_date, price, availibility, int(user)))
            conn.commit()
            cur.close()
            # return render_template('warehouse.html', itemlist=itemlist)
            return redirect('/warehouse/'+user)
        elif request.form['submit']=='Delete':
            delete = request.form.getlist('delete')
            cur = conn.cursor()
            for d in delete:
                cur.execute('delete from items where item_id = (%s)', (d,))
            conn.commit()
            cur.close()
            return redirect('/warehouse/' + user)
        else:
            return redirect('/view_orders/' +user)
    # if itemlist != None:
    # else:
    # return render_template('warehouse.html', itemlist=itemlist)
    else:
        cur = conn.cursor()
        user1 = int(user)
        cur.execute('select * from items where warehouse_id = (%s);', (user1,))
        # global itemlist
        itemlist = cur.fetchall()
        cur.close()
        return render_template('warehouse1.html', itemlist=itemlist, price_f =False)
        #     print('itemlist is none')
        #     return render_template('warehouse.html')

@app.route('/selectwarehouse/<int:user>',methods=['GET','POST'])
def selectwarehouse(user):
    if request.method=='GET':
        cur = conn.cursor()
        cur.execute('select * from warehouses')
        ware = cur.fetchall()
        cur.close
        return render_template('selectwarehouse1.html', ware = ware)
    else:
        # cur = conn.cursor()
        details = request.form
        id = details['select']
        return redirect('/selectitem/'+id+'/'+str(user))

@app.route('/selectitem/<int:id>/<int:user>', methods=['GET', 'POST'])
def selectitem(id, user):
    if request.method=='GET':
        cur = conn.cursor()
        cur.execute('select * from items where warehouse_id = (%s);', (id,))
        items = cur.fetchall()
        cur.close()
        return render_template('selectitem1.html', itemlist=items)
    else:
        cur = conn.cursor()
        items = request.form.getlist('select')
        quantity = request.form.getlist('quantity')
        print(items)
        print(quantity)
        table = "cart" + str(user)
        cur.execute('drop table if exists %(table)s', {"table":AsIs(table)})
        # cur.execute('drop table if exists %s')
        conn.commit()
        cur.execute('create table %(table)s (item_number serial primary key, item_id integer not null references items(item_id) on delete cascade , price integer not null, quantity integer not null, total integer generated always as (quantity*price) stored); ',{"table":AsIs(table)})
        conn.commit()
        for i in range(0, len(items)):
            cur.execute('select price from items where item_id = (%s)',(items[i],))
            price1 = cur.fetchone()[0]
            # cur.execute('insert into %(table)s (item_id,price, quantity) values (%s, %s,%s)', {"table":AsIs(table),items[i], price1,quantity[i]})
            try:
                cur.execute('insert into %s (item_id, price, quantity) values (%%s, %%s, %%s)' %table, (items[i], price1,quantity[i]))
                conn.commit()
            except:
                cur.close()
                return redirect('/selectitem/'+str(id)+'/'+str(user))
        cur.close()
        return redirect('/cart/'+str(id)+'/'+str(user))

@app.route('/cart/<int:ware_id>/<int:user>', methods=['GET','POST'])
def cart(user,ware_id):
    if request.method == 'GET':
        cur = conn.cursor()
        table = 'cart'+str(user)
        cur.execute('select * from %(table)s', {"table":AsIs(table)})
        items = cur.fetchall()
        cur.close()
        return render_template('cart1.html', list=items, order=False)
    else:
        if request.form['submit']=='Place Order':
            cur = conn.cursor()
            table = 'cart'+str(user)
            cur.execute('select * from %(table)s;',{"table":AsIs(table)})
            items = cur.fetchall()
            for i in items:
                cur.execute('delete from orders where item_id = (%s) and shop_id = (%s) and ware_id = (%s)', (i[1], user, ware_id))
                cur.execute('insert into orders(item_num, item_id, price, quantity, shop_id, ware_id) values(%s, %s, %s, %s, %s, %s)',(i[0], i[1],i[2],i[3],user, ware_id))
                conn.commit()
            cur.close
            return render_template('cart1.html', list=items, order=True)
        else:
            return redirect('/selectitem/'+str(ware_id)+'/'+str(user))

@app.route('/view_orders/<int:user>', methods=['GET','POST'])
def orders(user):
    if request.method == 'GET':
        cur=conn.cursor()
        cur.execute('drop view if exists orders_dis')
        conn.commit()
        cur.execute('create view orders_dis as select item_num, item_name, quantity, items.price, total, store_name, mobile from orders, items, users where orders.item_id = items.item_id and ware_id = (%s) and orders.shop_id=users.id;',(user,))
        conn.commit()
        # cur.execute('select * from orders where ware_id = (%s)', (user,))
        cur.execute('select * from orders_dis')
        orders = cur.fetchall()
        cur.close()
        return render_template('view_order1.html', orders = orders)
    else:
        cur = conn.cursor()
        complete = request.form.getlist('completed')
        for i in complete:
            cur.execute("delete from orders where ware_id = (%s) and item_id= (%s)", (user, i));
            conn.commit()
        cur.close()
        return redirect('/view_orders/'+str(user))

if __name__ == '__main__':
    app.run(debug=True)
