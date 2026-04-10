import SwiftUI

struct PairingView: View {
    @EnvironmentObject var api: APIClient
    @Environment(\.dismiss) var dismiss

    let device: Device
    var onPaired: () -> Void

    @State private var pin = ""
    @State private var message = ""
    @State private var isPairing = false
    @State private var errorMessage: String?
    @State private var phase: PairingPhase = .ready

    enum PairingPhase {
        case ready, waitingForPin, completed
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Image(systemName: "appletv.fill")
                    .font(.system(size: 60))
                    .foregroundColor(.blue)

                Text(device.name)
                    .font(.title2)
                    .bold()

                switch phase {
                case .ready:
                    Text("페어링을 시작하려면 아래 버튼을 탭하세요.")
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)

                    Button(action: startPairing) {
                        Label("페어링 시작", systemImage: "link")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isPairing)

                case .waitingForPin:
                    Text(message)
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)

                    TextField("PIN 입력", text: $pin)
                        .keyboardType(.numberPad)
                        .textFieldStyle(.roundedBorder)
                        .frame(width: 200)
                        .multilineTextAlignment(.center)
                        .font(.title)

                    Button(action: submitPin) {
                        Label("확인", systemImage: "checkmark.circle")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(pin.isEmpty || isPairing)

                case .completed:
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 40))
                        .foregroundColor(.green)
                    Text("페어링 완료!")
                        .font(.headline)
                }

                if isPairing {
                    ProgressView()
                }
            }
            .padding(32)
            .navigationTitle("페어링")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("취소") { dismiss() }
                }
            }
            .alert("오류", isPresented: .init(
                get: { errorMessage != nil },
                set: { if !$0 { errorMessage = nil } }
            )) {
                Button("확인") { errorMessage = nil }
            } message: {
                Text(errorMessage ?? "")
            }
        }
    }

    private func startPairing() {
        isPairing = true
        Task {
            do {
                let result = try await api.startPairing(deviceId: device.id)
                message = result.message ?? "Apple TV에 표시된 PIN을 입력하세요."
                phase = .waitingForPin
            } catch {
                errorMessage = error.localizedDescription
            }
            isPairing = false
        }
    }

    private func submitPin() {
        isPairing = true
        Task {
            do {
                let result = try await api.finishPairing(deviceId: device.id, pin: pin)
                if result.paired == true {
                    phase = .completed
                    try? await Task.sleep(nanoseconds: 1_000_000_000)
                    onPaired()
                } else {
                    errorMessage = "페어링에 실패했습니다. 다시 시도하세요."
                    phase = .ready
                }
            } catch {
                errorMessage = error.localizedDescription
                phase = .ready
            }
            isPairing = false
        }
    }
}
