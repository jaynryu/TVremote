import SwiftUI

struct RemoteView: View {
    @EnvironmentObject var api: APIClient

    let device: Device
    var onDisconnect: () -> Void

    @State private var showKeyboard = false
    @State private var statusText = ""
    @State private var feedbackScale: [String: CGFloat] = [:]

    var body: some View {
        VStack(spacing: 0) {
            // 상단: 기기 정보 + 상태
            VStack(spacing: 4) {
                Text(device.name)
                    .font(.headline)
                if !statusText.isEmpty {
                    Text(statusText)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
            .padding(.top, 8)

            Spacer()

            // 중앙: 방향키 + 선택
            VStack(spacing: 16) {
                remoteButton("chevron.up", command: "up")

                HStack(spacing: 40) {
                    remoteButton("chevron.left", command: "left")
                    selectButton()
                    remoteButton("chevron.right", command: "right")
                }

                remoteButton("chevron.down", command: "down")
            }

            Spacer()

            // 하단: 기능 버튼
            VStack(spacing: 16) {
                // 재생 컨트롤
                HStack(spacing: 32) {
                    actionButton("backward.end.fill", command: "previous", label: "이전")
                    actionButton("playpause.fill", command: "play_pause", label: "재생")
                    actionButton("forward.end.fill", command: "next", label: "다음")
                }

                // 네비게이션 버튼
                HStack(spacing: 24) {
                    actionButton("line.3.horizontal", command: "menu", label: "메뉴")
                    actionButton("house.fill", command: "home", label: "홈")
                    actionButton("keyboard", command: nil, label: "키보드") {
                        showKeyboard = true
                    }
                }

                // 볼륨
                HStack(spacing: 32) {
                    actionButton("speaker.minus.fill", command: "volume_down", label: "볼륨-")
                    actionButton("speaker.plus.fill", command: "volume_up", label: "볼륨+")
                }

                // 연결 해제
                Button(action: disconnect) {
                    Text("연결 해제")
                        .font(.footnote)
                        .foregroundColor(.red)
                }
                .padding(.top, 8)
            }
            .padding(.bottom, 24)
        }
        .padding(.horizontal)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showKeyboard) {
            KeyboardInputView()
        }
        .task {
            await refreshStatus()
        }
    }

    // MARK: - 방향키 버튼

    private func remoteButton(_ icon: String, command: String) -> some View {
        Button(action: { sendCommand(command) }) {
            Image(systemName: icon)
                .font(.system(size: 28, weight: .medium))
                .frame(width: 64, height: 64)
                .foregroundColor(.primary)
        }
        .scaleEffect(feedbackScale[command] ?? 1.0)
    }

    // MARK: - 선택 버튼

    private func selectButton() -> some View {
        Button(action: { sendCommand("select") }) {
            Circle()
                .fill(Color.blue.opacity(0.15))
                .frame(width: 80, height: 80)
                .overlay(
                    Text("OK")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.blue)
                )
        }
        .scaleEffect(feedbackScale["select"] ?? 1.0)
    }

    // MARK: - 기능 버튼

    private func actionButton(
        _ icon: String,
        command: String?,
        label: String,
        action: (() -> Void)? = nil
    ) -> some View {
        Button(action: {
            if let action = action {
                action()
            } else if let command = command {
                sendCommand(command)
            }
        }) {
            VStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 22))
                Text(label)
                    .font(.system(size: 10))
            }
            .frame(width: 56, height: 48)
            .foregroundColor(.primary)
        }
    }

    // MARK: - Actions

    private func sendCommand(_ command: String) {
        // 탭 피드백
        withAnimation(.easeInOut(duration: 0.1)) {
            feedbackScale[command] = 0.85
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            withAnimation(.easeInOut(duration: 0.1)) {
                feedbackScale[command] = 1.0
            }
        }

        Task {
            do {
                try await api.sendCommand(command)
            } catch {
                // 조용히 실패 (네트워크 지연 등)
            }
        }
    }

    private func disconnect() {
        Task {
            try? await api.disconnect(deviceId: device.id)
            onDisconnect()
        }
    }

    private func refreshStatus() async {
        do {
            let status = try await api.getStatus()
            if let title = status.title {
                statusText = title
                if let artist = status.artist {
                    statusText += " - \(artist)"
                }
            } else if let app = status.app {
                statusText = app
            }
        } catch {
            statusText = ""
        }
    }
}
