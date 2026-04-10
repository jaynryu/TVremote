import SwiftUI

struct DeviceListView: View {
    @EnvironmentObject var api: APIClient
    var onConnect: (Device) -> Void

    @State private var devices: [Device] = []
    @State private var isScanning = false
    @State private var errorMessage: String?
    @State private var pairingDevice: Device?
    @State private var showPairing = false

    var body: some View {
        List {
            if devices.isEmpty && !isScanning {
                ContentUnavailableView(
                    "기기를 찾지 못했습니다",
                    systemImage: "appletv",
                    description: Text("같은 네트워크에 Apple TV가 켜져 있는지 확인하세요.")
                )
            }

            ForEach(devices) { device in
                Button(action: { connectDevice(device) }) {
                    HStack {
                        Image(systemName: "appletv.fill")
                            .font(.title2)
                            .foregroundColor(.blue)
                        VStack(alignment: .leading) {
                            Text(device.name)
                                .font(.headline)
                            Text(device.address)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 4)
                }
            }
        }
        .navigationTitle("Apple TV 검색")
        .refreshable {
            await scanDevices()
        }
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                if isScanning {
                    ProgressView()
                } else {
                    Button(action: { Task { await scanDevices() } }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
        .task {
            await scanDevices()
        }
        .sheet(isPresented: $showPairing) {
            if let device = pairingDevice {
                PairingView(device: device, onPaired: {
                    showPairing = false
                    connectDevice(device)
                })
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

    private func scanDevices() async {
        isScanning = true
        defer { isScanning = false }
        do {
            devices = try await api.scanDevices()
        } catch {
            errorMessage = "검색 실패: \(error.localizedDescription)"
        }
    }

    private func connectDevice(_ device: Device) {
        Task {
            do {
                _ = try await api.connect(deviceId: device.id)
                onConnect(device)
            } catch {
                // 연결 실패 시 페어링 필요할 수 있음
                pairingDevice = device
                showPairing = true
            }
        }
    }
}
