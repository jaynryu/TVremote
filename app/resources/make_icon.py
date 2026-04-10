"""Apple TV Remote 앱 아이콘 생성 스크립트."""

from PIL import Image, ImageDraw, ImageFont
import subprocess
import tempfile
import os

SIZES = [16, 32, 64, 128, 256, 512, 1024]


def create_icon(size):
    """Apple TV 리모트 스타일 아이콘 생성."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 둥근 사각형 배경
    margin = int(size * 0.04)
    radius = int(size * 0.22)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        fill="#1c1c1e",
    )

    # 내부 패딩
    cx, cy = size // 2, size // 2

    # D-pad 원형 배경
    pad_r = int(size * 0.28)
    pad_cy = cy - int(size * 0.08)
    draw.ellipse(
        [cx - pad_r, pad_cy - pad_r, cx + pad_r, pad_cy + pad_r],
        fill="#2c2c2e",
    )

    # 중앙 OK 버튼
    ok_r = int(size * 0.10)
    draw.ellipse(
        [cx - ok_r, pad_cy - ok_r, cx + ok_r, pad_cy + ok_r],
        fill="#0a84ff",
    )

    # 방향 화살표 (삼각형)
    arrow_size = int(size * 0.06)
    arrow_offset = int(size * 0.20)

    # 위
    ax, ay = cx, pad_cy - arrow_offset
    draw.polygon(
        [(ax, ay - arrow_size), (ax - arrow_size, ay + arrow_size // 2), (ax + arrow_size, ay + arrow_size // 2)],
        fill="#8e8e93",
    )
    # 아래
    ax, ay = cx, pad_cy + arrow_offset
    draw.polygon(
        [(ax, ay + arrow_size), (ax - arrow_size, ay - arrow_size // 2), (ax + arrow_size, ay - arrow_size // 2)],
        fill="#8e8e93",
    )
    # 왼쪽
    ax, ay = cx - arrow_offset, pad_cy
    draw.polygon(
        [(ax - arrow_size, ay), (ax + arrow_size // 2, ay - arrow_size), (ax + arrow_size // 2, ay + arrow_size)],
        fill="#8e8e93",
    )
    # 오른쪽
    ax, ay = cx + arrow_offset, pad_cy
    draw.polygon(
        [(ax + arrow_size, ay), (ax - arrow_size // 2, ay - arrow_size), (ax - arrow_size // 2, ay + arrow_size)],
        fill="#8e8e93",
    )

    # 하단 버튼들 (재생 컨트롤)
    btn_y = cy + int(size * 0.26)
    btn_w = int(size * 0.12)
    btn_h = int(size * 0.08)
    btn_r = int(size * 0.03)
    gap = int(size * 0.16)

    for i, offset in enumerate([-gap, 0, gap]):
        bx = cx + offset
        draw.rounded_rectangle(
            [bx - btn_w // 2, btn_y - btn_h // 2, bx + btn_w // 2, btn_y + btn_h // 2],
            radius=btn_r,
            fill="#3a3a3c",
        )

    # 재생 삼각형 (가운데 버튼)
    ps = int(size * 0.025)
    draw.polygon(
        [(cx - ps, btn_y - ps), (cx - ps, btn_y + ps), (cx + ps, btn_y)],
        fill="#8e8e93",
    )

    return img


def make_icns(output_path):
    """여러 사이즈의 PNG를 .icns로 변환."""
    with tempfile.TemporaryDirectory() as tmpdir:
        iconset_dir = os.path.join(tmpdir, "icon.iconset")
        os.makedirs(iconset_dir)

        name_map = {
            16: "icon_16x16.png",
            32: "icon_16x16@2x.png",
            64: "icon_32x32@2x.png",
            128: "icon_128x128.png",
            256: "icon_128x128@2x.png",
            512: "icon_256x256@2x.png",
            1024: "icon_512x512@2x.png",
        }
        # 추가 사이즈
        extra_map = {
            32: "icon_32x32.png",
            256: "icon_256x256.png",
            512: "icon_512x512.png",
        }

        for s in SIZES:
            img = create_icon(s)
            if s in name_map:
                img.save(os.path.join(iconset_dir, name_map[s]))
            if s in extra_map:
                img.save(os.path.join(iconset_dir, extra_map[s]))

        subprocess.run(
            ["iconutil", "-c", "icns", iconset_dir, "-o", output_path],
            check=True,
        )
        print(f"아이콘 생성 완료: {output_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    make_icns(os.path.join(script_dir, "icon.icns"))
