import SwiftUI

struct KeyboardInputView: View {
    @EnvironmentObject var api: APIClient
    @Environment(\.dismiss) var dismiss

    @State private var text = ""
    @State private var isSending = false
    @FocusState private var isFocused: Bool

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("Apple TV에 전송할 텍스트를 입력하세요")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                TextField("텍스트 입력", text: $text)
                    .textFieldStyle(.roundedBorder)
                    .font(.title3)
                    .focused($isFocused)
                    .onSubmit {
                        sendText()
                    }

                HStack(spacing: 16) {
                    Button(action: clearText) {
                        Label("지우기", systemImage: "xmark.circle")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .disabled(isSending)

                    Button(action: sendText) {
                        Label("전송", systemImage: "paperplane.fill")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(text.isEmpty || isSending)
                }

                if isSending {
                    ProgressView()
                }

                Spacer()
            }
            .padding(24)
            .navigationTitle("키보드")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("닫기") { dismiss() }
                }
            }
            .onAppear {
                isFocused = true
            }
        }
    }

    private func sendText() {
        guard !text.isEmpty else { return }
        isSending = true
        Task {
            do {
                try await api.sendText(text)
                text = ""
            } catch {
                // 에러 처리
            }
            isSending = false
        }
    }

    private func clearText() {
        isSending = true
        Task {
            do {
                try await api.clearText()
                text = ""
            } catch {
                // 에러 처리
            }
            isSending = false
        }
    }
}
