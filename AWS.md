### Guide on how to set up and connect to an AWS database

1. After logging into your AWS account, click on **Services** on the top left portion of the screen. <br> <br> <img width="100%" alt="Screen Shot 2020-12-26 at 2 56 09 PM" src="https://user-images.githubusercontent.com/51253177/103160505-f667f880-478a-11eb-8a58-e88a551cc4a5.png">

2. Click on **EC2** under **Compute**. <br> <br> <img width="240" alt="Screen Shot 2020-12-26 at 3 31 11 PM" src="https://user-images.githubusercontent.com/51253177/103160920-90ca3b00-478f-11eb-8210-532ad938da35.png">

3. On the left column, scroll until you get to the **Network & Security** section. Click on **Security Groups**. <br> <br> <img width="240" alt="Screen Shot 2020-12-26 at 3 33 53 PM" src="https://user-images.githubusercontent.com/51253177/103161380-020cec80-4796-11eb-9bfe-827ec4e371d0.png">

4. Proceed by clicking on **Create security group**. <br> <br> <img width="100%" alt="Screen Shot 2020-12-26 at 4 21 41 PM" src="https://user-images.githubusercontent.com/51253177/103161429-91b29b00-4796-11eb-868a-1aa461f9d54d.png">

5. Enter the following sections and create a security group:
   * **Security group name**
   * **Description**
   * Under **Inbound** rules:  
     - **Type**- Set to MYSQL/Aurora.   
     - **Source**- Enter IP address with a "/32" at the end. To view your IP address, [click here](http://checkip.amazonaws.com/).
   * Under **Outbound** rules:  
     - **Source**- Enter IP address with a "/32" at the end. To view your IP address, [click here](http://checkip.amazonaws.com/).

6. Under the **Services** section from step 1, click on **RDS** under the **Database** section. <br> <br> <img width="240" alt="Screen Shot 2020-12-26 at 3 02 52 PM" src="https://user-images.githubusercontent.com/51253177/103160573-cd943300-478b-11eb-86e7-95687111f252.png">

7. On the page you are taken to, click on **Databases** in the column on the left side. <br> <br> <img width="240" alt="Screen Shot 2020-12-26 at 3 13 29 PM" src="https://user-images.githubusercontent.com/51253177/103160687-0ed91280-478d-11eb-90be-cac1624a265d.png">

8. Click on **Create Database** on the page that populates. <br> <br> <img width="100%" alt="Screen Shot 2020-12-26 at 3 17 02 PM" src="https://user-images.githubusercontent.com/51253177/103160793-ab9bb000-478d-11eb-8936-6e8ae2ce220c.png">

9. Follow these steps to create a database:
   * Under **Engine Options**, change **Engine Type** to MySql
   * Change to **Free tier** under **Templates**
   * Under **Settings**:  
     - **DB instance identifier**- Enter a database name you would like.  
     - **Master username**- Create a username. The username will be the user value in the awsDB python file.    
     - **Master password**- Create a password. The password will be the password value in the awsDB python file.
   * Under **Connectivity**:  
     - Change **Public Access** from No to Yes.  
     - Change the **Existing VPC security groups** from default to the security group created in step 5.
   * Under **Additional configuration**, set desired name for the **Initial database name** section. This will be the db value in the awsDB python file.

10. After the database is created, the host and port values can be obtained by going to the page from taking step 7. From there, click, on the name of the database you created. In the **Connectivity & security section**, the **Endpoint** will be the host value, and the port number should be shown right below.
