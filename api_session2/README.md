# BÀI 1
## Get danh sách rỗng 200 + POST OK 201
![alt text](result/app1_1.png)
## Gửi request không có Content-Type 415
![alt text](result/app1_2.png)
## Thiếu author 422
![alt text](result/app1_3.png)
# BÀI 2
## PATCH - cập nhật giá price của sách ID 1 thành 19.99
![alt text](result/app2_1.png)
## PUT - thay sách ID 1 bằng title và author khác
![alt text](result/app2_2.png)
## DELETE - Xoá cuốn sách ID 1
![alt text](result/app2_3.png)
# BÀI 3
## Phân trang (page = 2, size = 10)
![alt text](result/app3_1.png)
## Lọc theo tác giá (author = Orwell) 
![alt text](result/app3_2.png)
## Lọc theo từ khoá trong tiêu đề(q = clean)
![alt text](result/app3_3.png)
## Lọc theo header Accept
![alt text](result/app3_4.png)
## Vượt MAX_SIZE (tự động cap về 100)
![alt text](result/app3_5.png)