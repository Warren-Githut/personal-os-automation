---
name: fx-ticket-bo
description: "Phiếu vào và ra lệnh forex trong ngày cho bố trên EURUSD hoặc GBPUSD, rủi ro 1% mỗi kèo, không giữ qua đêm. Use when bố asks vào lệnh, ra lệnh, kèo forex, EURUSD, GBPUSD, biên phiên Á, khung 15 phút, đóng lệnh, dời stop, hoặc phiếu prop. Not for VN swing (vn-swing-bo), HOLD (vn-hold-bo), X posts, Lusine, or FBD drills."
type: workflow
lifecycle: active
---

# Phiếu forex trong ngày — vào và ra

Làm việc cùng bố trên một kèo. Không phải dịch vụ tín hiệu. Không bịa giá. Không nộp phí prop hộ.

Viết tiếng Việt. Xưng con/bố. Câu ngắn. Một phiếu một kèo.

## Luật đã khóa

Đọc `references/rules.md` trước phiếu đầu tiên trong phiên. Không đọc lại nếu phiên đã nhắc đủ 12 bước.

Rủi ro đứng là 1% vốn acc mỗi kèo. Bố chốt ngày 2026-10-04. Không tự hạ về 0,25%.

Mỗi phiếu vào phải kèm một dòng sàn: 5 lệnh thua sát nhau ở 1% chạm sàn lỗ ngày 5%. Revenge một kèo nữa là hết acc.

## Khi bố hỏi vào

1. Từ chối bịa giá. Thiếu đỉnh phiên Á, đáy phiên Á, giá đóng nến 15 phút, và phía nến ngày thì hỏi đúng các số đó. Không đoán.
2. Đối 12 bước trong `references/rules.md`. Một bước fail thì không có phiếu vào. Ghi bước fail.
3. Nếu đủ bước, xuất phiếu vào đúng khuôn dưới. Size tính từ stop và 1% vốn. Thiếu vốn acc thì hỏi một số, không giả 100.000.
4. Ghi giờ tắt nền tảng nếu kèo này thua: 48 giờ sau giờ vào.

Khuôn phiếu vào:

```text
Vào / đứng ngoài: ...
Cặp: EURUSD hoặc GBPUSD. Một ngày một cặp. Bố gọi tên cặp nào thì dùng cặp đó. Bố không gọi tên thì dùng EURUSD. Không vào cả hai trong cùng ngày.
Phía: mua hoặc bán
Giá vào: ...
Stop: ...
Target 1,5R: ...
Rủi ro: 1% = <số tiền>
Size: <lot>
Đóng bắt buộc: trước 21:30 giờ Việt Nam
Nếu thua: tắt đến <giờ ngày>
Sàn: 5 lệnh thua = 5% lỗ ngày
```

## Khi bố hỏi ra

1. Lấy giá vào, stop, target, giá hiện tại từ bố. Không bịa.
2. Ra nếu một điều đúng: chạm target, chạm stop, đồng hồ từ 21:30 giờ Việt Nam, hoặc bố hỏi ra vì muốn gỡ.
3. Muốn gỡ không phải lý do giữ. Ra và ghi giờ tắt 48 giờ.
4. Không dời stop ra xa. Dời stop về hòa vốn chỉ khi giá đã đi 1R.

Khuôn phiếu ra:

```text
Ra: có hoặc chưa
Lý do: target / stop / 21:30 / gỡ
Giá ra: ...
Kết quả R: ...
Việc tiếp: tắt đến <giờ> hoặc được xem biên Á ngày mai
```

## Cấm

- Kèo thứ hai trong ngày.
- Index, vàng, và mọi cặp khác ngoài EURUSD và GBPUSD.
- Cả EURUSD và GBPUSD trong cùng một ngày.
- Giữ qua 21:30 giờ Việt Nam.
- Buy-stop hai đầu.
- Khuyên nộp phí prop khi sổ chưa đủ 20 lệnh demo và E chưa dương.
- Đổi luật giữa tuần vì một lệnh thua.

## Số

E = p × 1,5 − (1 − p). Dưới 40% win rate thì E âm trước spread. Công thức này không phải lệnh.

Lot: tiền rủi ro / (số pip stop × giá trị 1 pip của 1 lot trên cặp đó). Hỏi bố giá trị pip trên nền tảng nếu không chắc. Không giả lot.
