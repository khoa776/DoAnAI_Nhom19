# ĐỒ AN MÔN TRÍ TUỆ NHÂN TẠO NHÓM 19: ROBOT GIAO HÀNG

ChronoCourier là game robot giao hàng được viết bằng Python và Pygame. Game gồm 6 level, mỗi level minh họa một nhóm thuật toán AI khác nhau. Robot di chuyển trên bản đồ dạng ô vuông, giao hàng đến các điểm yêu cầu và xử lý thêm các cơ chế như pin, trạm sạc, môi trường mất tín hiệu, ràng buộc thứ tự và boss truy đuổi.

## Cách chạy

```bash
Tại thư mục game
py -3 main.py
```
hoặc sử dụng icon game

## Điều khiển cơ bản

- Phím mũi tên: điều khiển robot thủ công.
- Chọn thuật toán trên bảng điều khiển.
- `CHAY AI`: chạy thuật toán đang chọn.
- `RESET`: chạy lại level hiện tại.
- `DOI MAP`: đổi map nếu level có nhiều map.
- `DOI MAN`: chuyển sang level tiếp theo.

Khi chạy thuật toán, game sẽ tìm đường trước, sau đó robot di chuyển theo đường kết quả cuối cùng.

## Nội dung các level

 Level 1  Giao tất cả món hàng, không xét pin và chi phí ô.  (BFS, DFS) 
 Level 2  Giao hàng có pin, trạm sạc và ô tốn 2 pin.  (Greedy, A*) 
 Level 3  Giao hàng qua mê cung, có trường hợp dễ kẹt cực trị cục bộ.  (Simple Hill Climbing, Simulated Annealing) 
 Level 4  Giao hàng trong môi trường mất tín hiệu, robot không biết trước vị trí goal.  (tìm kiếm mù với BFS, DFS) 
 Level 5  Giao hàng theo đúng thứ tự ràng buộc.  (Backtracking, Forward Checking) 
 Level 6  Giao hàng và tránh vùng nguy hiểm của boss.  (Minimax, Alpha-Beta) 

## Cấu trúc thư mục

```text
DoAnAI/
├── main.py
├── config.py
├── algorithms/
├── data/
├── screens/
├── ui/
├── audio/
├── assets/
└── docs/
```

## Công dụng các phần chính

- `main.py`: file chạy chương trình. Tạo game và gọi `Game().run()`.
- `config.py`: lưu cấu hình chung như kích thước màn hình, kích thước ô, màu sắc, FPS.
- `data/maps.py`: lưu toàn bộ map, vị trí robot, điểm giao hàng, trạm sạc, laser, boss và các hàm kiểm tra ô đi được.
- `screens/manual_map.py`: màn hình chính của game. File này xử lý vẽ map, bảng điều khiển, đổi level, đổi map, chạy thuật toán và cho robot di chuyển theo kết quả.
- `ui/drawing.py`: các hàm vẽ chữ, căn giữa chữ, xuống dòng chữ.
- `ui/sprites.py`: các hàm vẽ robot, pin, trạm sạc và một số hình phụ trợ.
- `audio/sound_manager.py`: xử lý nhạc nền.
- `assets/`: chứa ảnh dùng trong game, ví dụ ảnh boss và robot ở level 6.
- `docs/`: chứa tài liệu ghi chú, tổng quan ý tưởng và cấu trúc project.

## Các file thuật toán

- `algorithms/search_common.py`: hàm dùng chung cho BFS và DFS ở level 1.
- `algorithms/bfs.py`: thuật toán BFS cho level 1.
- `algorithms/dfs.py`: thuật toán DFS cho level 1.
- `algorithms/informed_common.py`: hàm dùng chung cho Greedy và A* ở level 2.
- `algorithms/greedy.py`: thuật toán Greedy Best-First Search.
- `algorithms/astar.py`: thuật toán A* với `f(n) = g(n) + h(n)`.
- `algorithms/local_search.py`: Simple Hill Climbing và Simulated Annealing cho level 3.
- `algorithms/belief_search.py`: BFS và DFS cho level 4 trong môi trường mất tín hiệu.
- `algorithms/csp_backtracking.py`: Backtracking và Forward Checking cho level 5.
- `algorithms/adversarial_search.py`: Minimax và Alpha-Beta cho level 6.

Một số file backup của `belief_search` được giữ lại để tham khảo phiên bản cũ, nhưng game hiện tại dùng file `algorithms/belief_search.py`.

## Ký hiệu map thường gặp

- `F`: sàn đi được.
- `W`: tường, không đi được.
- `X`: thùng hoặc chướng ngại vật, không đi được.
- `.`: hố hoặc vùng trống, không đi được.
- Ô laser: không đi được.
- Ô giao hàng: nơi robot cần đi tới để giao món hàng.
- Trạm sạc: dùng ở level 2 để hồi pin cho robot.

## Thông tin hiển thị khi chạy thuật toán

Trên bảng điều khiển, game hiển thị các thông tin chính như:

- Thời gian chạy thuật toán.
- Số node đã xét.
- Số bước trong đường đi kết quả.
- Với level 2 có thêm pin và lượng pin đã tiêu thụ.
- Với level 5 có thêm danh sách ràng buộc.

Các thông tin này dùng để quan sát và so sánh thuật toán trong báo cáo.
