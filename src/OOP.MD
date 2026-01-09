# OOP
## Đóng gói

### Từ khoá truy cập
    - private
    - public
    - protected 
    private (public getter, setter)
    public cho phép truy cập thoải mái
    protected 
## Kế thừa:
    - Có đa kế thừa không?
    - Lớp trừu tượng (Abstract class), Interface
    - Kế thừa nhiều cấp 
    - Thế nào là Abstract class? Interface? 
    - C# hoặc Java
    

```csharp
interface IProductRepository
{
    //CRUD object 
    Product add(Product product);
    int update(Product product, int id);
    bool delete(int id);
}
class ProductRepository implements IProductRepository
{
    public Product add(Product product)
    {
    }
    public int update(Product product, int id)
    {
    }
    public bool delete(int id)
    {
    }
}
```


Interface 
Cho phép khai báo các phương thức 
- Kiểu dữ liệu trả về 
- Danh sách tham số 

```csharp
interface ITodoRepository
{
    Todo add(Todo todo);
    bool update(Todo todo, int id);
    bool delete(int id);
}


```

