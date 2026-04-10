import SwiftUI

struct ContentView: View {
    @EnvironmentObject var api: APIClient
    @State private var connectedDevice: Device?
    @State private var showSettings = false

    var body: some View {
        NavigationStack {
            Group {
                if let device = connectedDevice {
                    RemoteView(device: device, onDisconnect: {
                        connectedDevice = nil
                    })
                } else {
                    DeviceListView(onConnect: { device in
                        connectedDevice = device
                    })
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showSettings = true }) {
                        Image(systemName: "gear")
                    }
                }
            }
        }
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
    }
}

struct SettingsView: View {
    @EnvironmentObject var api: APIClient
    @Environment(\.dismiss) var dismiss
    @State private var urlText = ""
    @State private var healthOk: Bool?

    var body: some View {
        NavigationStack {
            Form {
                Section("서버 주소") {
                    TextField("http://192.168.0.100:8000", text: $urlText)
                        .autocapitalization(.none)
                        .keyboardType(.URL)
                }

                Section {
                    Button("연결 테스트") {
                        Task {
                            api.serverURL = urlText
                            do {
                                healthOk = try await api.healthCheck()
                            } catch {
                                healthOk = false
                            }
                        }
                    }

                    if let ok = healthOk {
                        Text(ok ? "연결 성공" : "연결 실패")
                            .foregroundColor(ok ? .green : .red)
                    }
                }
            }
            .navigationTitle("설정")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("완료") {
                        api.serverURL = urlText
                        dismiss()
                    }
                }
            }
            .onAppear {
                urlText = api.serverURL
            }
        }
    }
}
