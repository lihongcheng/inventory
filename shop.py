import tkinter as tk
from tkinter import ttk
import sqlite3
import tkinter.messagebox as messagebox


class LoginWindow:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        master.title("登录")

        self.create_widgets()

    def create_widgets(self):
        self.username_label = tk.Label(self.master, text="用户名:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.password_label = tk.Label(self.master, text="密码:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = tk.Entry(self.master)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        self.login_button = tk.Button(self.master, text="登录", command=self.login)
        self.login_button.grid(row=2, column=1, pady=10)

    def login(self):
        # Replace with your actual authentication logic
        # For example, check if the username and password match a predefined admin user
        if self.username_entry.get() == "admin" and self.password_entry.get() == "admin":
            self.app.show_main_interface()
            self.master.destroy()  # Withdraw (hide) the login window
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")


class MobileInventorySystem:
    def __init__(self, master):
        self.master = master
        master.title("手机商品进销存系统")

        # 创建数据库连接
        self.conn = sqlite3.connect("mobile_inventory.db")
        self.cursor = self.conn.cursor()

        # 创建商品表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                purchase_quantity INTEGER NOT NULL,
                sale_quantity INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

        # Initialize login window
        self.login_window = LoginWindow(tk.Toplevel(master), self)

    def show_main_interface(self):
        self.create_main_interface_widgets()
        self.page_size = 5  # Number of products per page
        self.current_page = 1
        # Display the product list on startup
        self.display_product_list()

    def create_main_interface_widgets(self):
        # Create the search entry and button
        self.search_entry = tk.Entry(self.master, width=20)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)  # Moved to column 1

        # Set placeholder text
        self.search_entry.insert(0, "商品名称或ID")

        # Bind the click event to remove placeholder text
        self.search_entry.bind("<FocusIn>", self.on_search_entry_click)

        # Bind the focus out event to restore placeholder text
        self.search_entry.bind("<FocusOut>", self.on_search_entry_focus_out)

        search_button = tk.Button(self.master, text="搜索", command=self.display_search_results)
        search_button.grid(row=0, column=2, padx=10, pady=10)  # Moved to column 2

        # Create the function menu
        self.menu_label = tk.Label(self.master, text="功能菜单", font=('Helvetica', 16, 'bold'))
        self.menu_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.manage_button = tk.Button(self.master, text="管理商品", command=self.manage_products)
        self.manage_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.purchase_button = tk.Button(self.master, text="进货", command=self.purchase_products)
        self.purchase_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.sell_button = tk.Button(self.master, text="销货", command=self.sell_products)
        self.sell_button.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.check_button = tk.Button(self.master, text="查货", command=self.check_products)
        self.check_button.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.exit_button = tk.Button(self.master, text="退出", command=self.logout)
        self.exit_button.grid(row=7, column=3, padx=10, pady=10)

        # Create a Treeview widget to display the product list
        self.product_treeview = ttk.Treeview(self.master, columns=("ID", "名称", "价格", "数量"))
        self.product_treeview['show'] = 'headings'
        self.product_treeview.heading("ID", text="ID")
        self.product_treeview.heading("名称", text="名称")
        self.product_treeview.heading("价格", text="价格")
        self.product_treeview.heading("数量", text="数量")
        self.product_treeview.grid(row=2, column=1, rowspan=4, padx=10, pady=10, sticky="w")

        # Create pagination buttons
        prev_button = tk.Button(self.master, text="上一页", command=self.prev_page)
        prev_button.grid(row=7, column=1, padx=10, pady=10)

        next_button = tk.Button(self.master, text="下一页", command=self.next_page)
        next_button.grid(row=7, column=2, padx=10, pady=10)
        # Create labels for pagination information
        self.total_items_label = tk.Label(self.master, text="总条数：")
        self.total_items_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

        self.total_pages_label = tk.Label(self.master, text="共几页：")
        self.total_pages_label.grid(row=8, column=1, padx=10, pady=5)

        self.current_page_label = tk.Label(self.master, text="当前第几页：")
        self.current_page_label.grid(row=8, column=2, padx=10, pady=5)

    def on_search_entry_click(self, event):
        # Remove the placeholder text when the search entry is clicked
        if self.search_entry.get() == "商品名称或ID":
            self.search_entry.delete(0, tk.END)

    def on_search_entry_focus_out(self, event):
        # Restore the placeholder text when the focus is out and the entry is empty
        if not self.search_entry.get():
            self.search_entry.insert(0, "商品名称或ID")

    def display_search_results(self):
        search_query = self.search_entry.get()
        if search_query == "商品名称或ID":
            search_query = ""
        self.display_product_list(search_query)

    def display_product_list(self, search_query=None):
        # Clear any existing products in the treeview
        for item in self.product_treeview.get_children():
            self.product_treeview.delete(item)

        # Fetch and display products based on the search query
        if search_query:
            self.cursor.execute("SELECT id,name,price,quantity FROM products WHERE LOWER(name) LIKE LOWER(?) OR id=?",
                                ('%' + search_query + '%', search_query))
        else:
            offset = (self.current_page - 1) * self.page_size
            self.cursor.execute("SELECT id,name,price,quantity FROM products LIMIT ? OFFSET ?",
                                (self.page_size, offset))
            # self.cursor.execute("SELECT * FROM products")

        products = self.cursor.fetchall()

        for index, product in enumerate(products, 1):
            self.product_treeview.insert("", index, values=product)

        self.update_pagination_labels()

    def update_pagination_labels(self):
        # Get the total number of items
        self.cursor.execute("SELECT COUNT(*) FROM products")
        total_items = self.cursor.fetchone()[0]

        # Calculate the total number of pages
        total_pages = (total_items + self.page_size - 1) // self.page_size

        # Update labels
        self.total_items_label.config(text=f"总条数：{total_items}")
        self.total_pages_label.config(text=f"总页数：{total_pages}")
        self.current_page_label.config(text=f"当前页数：{self.current_page}")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_product_list()

    def next_page(self):
        # Check if there are more products to display
        self.cursor.execute("SELECT COUNT(*) FROM products")
        total_products = self.cursor.fetchone()[0]

        if (self.current_page * self.page_size) < total_products:
            self.current_page += 1
            self.display_product_list()

    def manage_products(self):
        # Create a new window for managing products
        manage_window = tk.Toplevel(self.master)
        manage_window.title("管理商品")

        # Define and display labels and entry widgets for product details
        tk.Label(manage_window, text="商品ID:").grid(row=0, column=0)
        product_id_entry = tk.Entry(manage_window)
        product_id_entry.grid(row=0, column=1)

        tk.Label(manage_window, text="商品名称:").grid(row=1, column=0)
        product_name_entry = tk.Entry(manage_window)
        product_name_entry.grid(row=1, column=1)

        tk.Label(manage_window, text="商品价格:").grid(row=2, column=0)
        product_price_entry = tk.Entry(manage_window)
        product_price_entry.grid(row=2, column=1)

        tk.Label(manage_window, text="商品数量:").grid(row=3, column=0)
        product_quantity_entry = tk.Entry(manage_window)
        product_quantity_entry.grid(row=3, column=1)

        # Define buttons for adding, deleting, and modifying products
        add_button = tk.Button(manage_window, text="新增商品",
                               command=lambda: self.add_product(product_name_entry.get(), product_price_entry.get(),
                                                                product_quantity_entry.get()))
        add_button.grid(row=4, column=0, columnspan=2, pady=5)

        delete_button = tk.Button(manage_window, text="删除商品",
                                  command=lambda: self.delete_product(product_id_entry.get()))
        delete_button.grid(row=5, column=0, columnspan=2, pady=5)

        modify_button = tk.Button(manage_window, text="修改商品",
                                  command=lambda: self.modify_product(product_id_entry.get(), product_name_entry.get(),
                                                                      product_price_entry.get(),
                                                                      product_quantity_entry.get()))
        modify_button.grid(row=6, column=0, columnspan=2, pady=5)

    def add_product(self, name, price, quantity):
        try:
            # Convert price and quantity to integers
            price = int(price)
            quantity = int(quantity)

            if price < 0 or quantity < 0:
                raise ValueError("数值不得为负数")

            # Insert a new product into the database
            self.cursor.execute("INSERT INTO products (name, price, quantity, purchase_quantity, sale_quantity) VALUES (?, ?, ?, 0, 0)",
                                (name, price, quantity))
            self.conn.commit()

            messagebox.showinfo("成功", "商品添加成功")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的价格和数量")

    def delete_product(self, product_id):
        try:
            # Convert product_id to integer
            product_id = int(product_id)

            # Check if the product exists
            self.cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
            product = self.cursor.fetchone()

            if product:
                # Delete the product from the database
                self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
                self.conn.commit()
                messagebox.showinfo("成功", "商品删除成功")
            else:
                messagebox.showerror("错误", "找不到该商品")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的商品ID")

    def modify_product(self, product_id, name, price, quantity):
        try:
            # Convert product_id, price, and quantity to integers
            product_id = int(product_id)
            price = int(price)
            quantity = int(quantity)
            if price < 0 or quantity < 0:
                raise ValueError("数值不得为负数")

            # Check if the product exists
            self.cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
            product = self.cursor.fetchone()

            if product:
                # Modify product information in the database
                self.cursor.execute("UPDATE products SET name=?, price=?, quantity=? WHERE id=?",
                                    (name, price, quantity, product_id))
                self.conn.commit()
                messagebox.showinfo("成功", "商品信息修改成功")
            else:
                messagebox.showerror("错误", "找不到该商品")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的商品ID、价格和数量")

    def purchase_products(self):
        # Create a new window for purchasing products
        purchase_window = tk.Toplevel(self.master)
        purchase_window.title("进货")

        # Define and display labels and entry widgets for purchase details
        tk.Label(purchase_window, text="商品ID:").grid(row=0, column=0)
        product_id_entry = tk.Entry(purchase_window)
        product_id_entry.grid(row=0, column=1)

        tk.Label(purchase_window, text="进货数量:").grid(row=1, column=0)
        purchase_quantity_entry = tk.Entry(purchase_window)
        purchase_quantity_entry.grid(row=1, column=1)

        # Define a button for purchasing products
        purchase_button = tk.Button(purchase_window, text="确认进货", command=lambda: self.confirm_purchase(
            product_id_entry.get(), purchase_quantity_entry.get()))
        purchase_button.grid(row=2, column=0, columnspan=2, pady=5)

        # Check if the product exists when the purchase button is clicked
        def on_purchase_button_click():
            entered_product_id = product_id_entry.get()
            self.cursor.execute("SELECT * FROM products WHERE id=?", (entered_product_id,))
            product = self.cursor.fetchone()

            if product:
                # Confirm purchase within this function
                self.confirm_purchase(entered_product_id, purchase_quantity_entry.get())
                purchase_window.destroy()
            else:
                manage_prompt = messagebox.askquestion("商品不存在", "该商品不存在，是否进入管理商品功能？")
                if manage_prompt == "yes":
                    if purchase_window.winfo_exists():  # Check if the window still exists
                        purchase_window.destroy()
                    self.manage_products()

        purchase_button.config(command=on_purchase_button_click)

    def confirm_purchase(self, product_id, quantity):
        try:
            # Convert product_id and quantity to integers
            product_id = int(product_id)
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("数值不得为负数")

            # Check if the product exists
            self.cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
            product = self.cursor.fetchone()

            if product:
                # Update the quantity of purchased products in the database
                new_quantity = product[3] + quantity  # current quantity + purchased quantity
                into_quantity = product[4] + quantity  # current quantity + purchased quantity
                self.cursor.execute("UPDATE products SET quantity=?,purchase_quantity=? WHERE id=?", (new_quantity,into_quantity, product_id))
                self.conn.commit()
                messagebox.showinfo("成功", f"{quantity}件商品进货成功")
            else:
                messagebox.showerror("错误", "找不到该商品")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的商品ID和进货数量")

    def sell_products(self):
        # Create a new window for selling products
        sell_window = tk.Toplevel(self.master)
        sell_window.title("销货")

        # Define and display labels and entry widgets for sale details
        tk.Label(sell_window, text="商品ID:").grid(row=0, column=0)
        product_id_entry = tk.Entry(sell_window)
        product_id_entry.grid(row=0, column=1)

        tk.Label(sell_window, text="销售数量:").grid(row=1, column=0)
        sale_quantity_entry = tk.Entry(sell_window)
        sale_quantity_entry.grid(row=1, column=1)

        # Define a button for selling products
        sell_button = tk.Button(sell_window, text="确认销售", command=lambda: self.confirm_sale(
            product_id_entry.get(), sale_quantity_entry.get()))
        sell_button.grid(row=2, column=0, columnspan=2, pady=5)

    def confirm_sale(self, product_id, quantity):
        try:
            # Convert product_id and quantity to integers
            product_id = int(product_id)
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("数值不得为负数")

            # Check if the product exists
            self.cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
            product = self.cursor.fetchone()

            if product:
                # Check if there is enough quantity to sell
                if product[3] >= quantity:
                    # Update the quantity of sold products in the database
                    new_quantity = product[3] - quantity  # current quantity - sold quantity
                    new_sale_quantity = product[5] + quantity
                    self.cursor.execute("UPDATE products SET quantity=?, sale_quantity=? WHERE id=?", (new_quantity, new_sale_quantity, product_id))
                    self.conn.commit()
                    messagebox.showinfo("成功", f"{quantity}件商品销售成功")
                else:
                    messagebox.showerror("错误", "库存不足，无法完成销售")
            else:
                messagebox.showerror("错误", "找不到该商品")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的商品ID和销售数量")

    def check_products(self):
        # Create a new window for checking products
        check_window = tk.Toplevel(self.master)
        check_window.title("查货")

        # Define and display labels and entry widgets for search details
        tk.Label(check_window, text="商品名称或ID:").grid(row=0, column=0)
        search_entry = tk.Entry(check_window)
        search_entry.grid(row=0, column=1)

        # Define a button for searching products
        search_button = tk.Button(check_window, text="查询",
                                  command=lambda: self.show_search_results(search_entry.get(), check_window))
        search_button.grid(row=1, column=0, columnspan=2, pady=5)

    def show_search_results(self, search_query, check_window):
        self.cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?) OR id=?",
                            ('%' + search_query + '%', search_query))
        search_results = self.cursor.fetchall()

        if search_results:
            check_window.destroy()
            sell_prompt = messagebox.askquestion("查询结果", "查询到商品，是否进入销货系统？")
            if sell_prompt == "yes":
                self.sell_products()
            else:
                self.show_product_details(search_results[0])
        else:
            messagebox.showinfo("结果", "未找到匹配的商品")

    def show_product_details(self, product):
        # Create a new window for displaying product details
        details_window = tk.Toplevel(self.master)
        details_window.title("商品详情")

        # Configure grid layout
        details_window.columnconfigure(0, weight=1)
        details_window.columnconfigure(1, weight=3)
        details_window.geometry("300x150")  # Adjust the size as needed

        # Display labels and values for product details
        tk.Label(details_window, text="商品ID:", font=('Helvetica', 12)).grid(row=0, column=0, sticky="w", padx=10,
                                                                              pady=5)
        tk.Label(details_window, text=product[0], font=('Helvetica', 12)).grid(row=0, column=1, sticky="w", padx=10,
                                                                               pady=5)

        tk.Label(details_window, text="商品名称:", font=('Helvetica', 12)).grid(row=1, column=0, sticky="w", padx=10,
                                                                                pady=5)
        tk.Label(details_window, text=product[1], font=('Helvetica', 12)).grid(row=1, column=1, sticky="w", padx=10,
                                                                               pady=5)

        tk.Label(details_window, text="商品价格:", font=('Helvetica', 12)).grid(row=2, column=0, sticky="w", padx=10,
                                                                                pady=5)
        tk.Label(details_window, text=product[2], font=('Helvetica', 12)).grid(row=2, column=1, sticky="w", padx=10,
                                                                               pady=5)

        tk.Label(details_window, text="商品数量:", font=('Helvetica', 12)).grid(row=3, column=0, sticky="w", padx=10,
                                                                                pady=5)
        tk.Label(details_window, text=product[3], font=('Helvetica', 12)).grid(row=3, column=1, sticky="w", padx=10,
                                                                               pady=5)

        tk.Label(details_window, text="进货数量:", font=('Helvetica', 12)).grid(row=4, column=0, sticky="w", padx=10,
                                                                                pady=5)
        tk.Label(details_window, text=product[4], font=('Helvetica', 12)).grid(row=4, column=1, sticky="w", padx=10,
                                                                               pady=5)

        tk.Label(details_window, text="销售数量:", font=('Helvetica', 12)).grid(row=5, column=0, sticky="w", padx=10,
                                                                                pady=5)
        tk.Label(details_window, text=product[5], font=('Helvetica', 12)).grid(row=5, column=1, sticky="w", padx=10,
                                                                               pady=5)

    def search_products(self, search_query):
        try:
            # Check if the search query is a number (considered as product ID)
            if search_query.isdigit():
                search_query = int(search_query)
                self.cursor.execute("SELECT * FROM products WHERE id=?", (search_query,))
            else:
                # Perform a case-insensitive fuzzy search for product names
                self.cursor.execute("SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)",
                                    ('%' + search_query + '%',))

            products = self.cursor.fetchall()

            if products:
                # Display the search results
                self.show_search_results(products)
            else:
                messagebox.showinfo("结果", "未找到匹配的商品")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的商品ID或商品名称")

    def logout(self):
        # Hide the main interface and show the login window
        self.master.destroy()  # Destroy the main window

    def __del__(self):
        # 关闭数据库连接
        self.conn.close()


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = MobileInventorySystem(root)
    root.mainloop()
