# AI Courier: Phong Thi Nghiem Mat Kiem Soat

Game gom 6 man. Tat ca cung mot boi canh: robot giao hang trong phong thi nghiem.
Moi man thay doi dieu kien de phu hop voi mot nhom thuat toan AI.

## Man 1 - Khong Co Thong Tin

- Thuat toan: BFS, DFS
- Noi dung: robot giao hang tren map khong co chi phi o, khong xet pin.
- BFS tim duong ngan nhat theo so buoc.
- DFS di sau truoc, co the tim duong dai hon.

## Man 2 - Co Thong Tin

- Thuat toan: Greedy, A*
- Noi dung: robot giao hang tren map co chi phi o va heuristic.
- g(n): so pin da tieu.
- h(n): khoang cach Manhattan toi dich.
- Greedy chon h(n) nho nhat.
- A* chon f(n) = g(n) + h(n).

## Man 3 - Local Search

- Thuat toan: Simple Hill Climbing, Simulated Annealing
- Noi dung: dat tram sac phu sao cho robot giao hang hieu qua hon.
- State: vi tri cac tram sac.
- Neighbor: di chuyen mot tram sac len/xuong/trai/phai.
- Score: so don giao duoc hoac tong quang duong cang nho cang tot.

## Man 4 - Moi Truong Phuc Tap

- Thuat toan: Belief-State Search, AND-OR Search
- Noi dung: robot bi mu mot phan, khong thay het map hoac khong chac vi tri.
- Belief state la tap cac vi tri co the.
- AND-OR tao ke hoach co dieu kien theo cam bien.

## Man 5 - CSP

- Thuat toan: Backtracking, Min-Conflicts
- Noi dung: lap thu tu giao hang theo rang buoc.
- Vi du: A phai giao truoc B, C khong duoc giao ngay sau D.
- Backtracking gan tung don vao tung slot.
- Min-Conflicts sua thu tu hien tai de giam xung dot.

## Man 6 - Doi Khang

- Thuat toan: Minimax, Alpha-Beta
- Noi dung: robot giao hang nhung co AI bao ve duoi/cham duong.
- Hai ben di theo luot.
- Minimax chon nuoc di tot nhat.
- Alpha-Beta cat tia de xet it node hon.
