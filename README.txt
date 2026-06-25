DoAnAI - AI Courier Prototype

Cach chay:
  cd /d D:\DoAnAI
  py -3 main.py

Noi dung:
- Co 3 map ma tran phong thi nghiem/sci-fi, moi map kich thuoc 11 x 20.
- Giao dien gon hon, panel dieu khien nam rieng ben phai.
- Robot co the di chuyen bang phim mui ten.
- Co nut RESET tren panel de dua robot ve ban dau.
- Panel co chon thuat toan BFS/DFS, nut CHAY AI, vi tri, duong da di, ket qua va danh sach hang can giao.
- Nut DOI MAP dung de chuyen qua map tiep theo, robot se reset ve diem bat dau cua map moi.
- Nut DOI MAN dung de chuyen giua man 1 va man 2.
- Nut QUA MAN va cac o chuc nang dang de san, se gan chuc nang sau.
- Co 4 diem giao hang A/B/C/D nam gan ria map: thuoc, may tinh, oc vit, chip.
- Vat can gom hop X, ho den dang o trong va tia laser giua hai hop cung hang/cot.
- Man 1 da gan BFS va DFS de tim duong giao du 4 mon, khong dung pin.
- Man 2 da co giao dien pin, tram sac va cac o vang ton 2 pin.
- Khi ket thuc se hien ket qua Hoan thanh hoac That bai tren bang dieu khien.
- Co nhac nen sci-fi, duoc bat trong audio\sound_manager.py.

File nen mo khi giai thich:
- docs\tong_quan_6_man.md: tom tat y tuong 6 man.
- docs\cau_truc_project.md: giai thich cau truc folder.
- data\maps.py: ma tran ban do.
- screens\manual_map.py: man hinh ve map va robot.
- audio\sound_manager.py: mo nhac nen cho game.
- ui\sprites.py: ve robot phu tro va tram sac.

Ky hieu trong code:
- F: san kim loai
- X: hop/chuong ngai vat, khong di duoc
- W: tuong
- .: ho/vung trong, khong di duoc
