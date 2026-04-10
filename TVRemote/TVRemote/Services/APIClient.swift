import Foundation

class APIClient: ObservableObject {
    @Published var serverURL: String {
        didSet {
            UserDefaults.standard.set(serverURL, forKey: "serverURL")
        }
    }

    init() {
        self.serverURL = UserDefaults.standard.string(forKey: "serverURL") ?? "http://192.168.0.100:8000"
    }

    private var baseURL: URL {
        URL(string: serverURL)!
    }

    // MARK: - Devices

    func scanDevices() async throws -> [Device] {
        let data = try await get(path: "/devices")
        let response = try JSONDecoder().decode(DevicesResponse.self, from: data)
        return response.devices
    }

    func startPairing(deviceId: String, protocol: String = "companion") async throws -> PairResponse {
        let body = ["protocol": `protocol`]
        let data = try await post(path: "/devices/\(deviceId)/pair", body: body)
        return try JSONDecoder().decode(PairResponse.self, from: data)
    }

    func finishPairing(deviceId: String, pin: String) async throws -> PairResponse {
        let body = ["pin": pin]
        let data = try await post(path: "/devices/\(deviceId)/pair/pin", body: body)
        return try JSONDecoder().decode(PairResponse.self, from: data)
    }

    func connect(deviceId: String) async throws -> CommandResponse {
        let data = try await post(path: "/devices/\(deviceId)/connect")
        return try JSONDecoder().decode(CommandResponse.self, from: data)
    }

    func disconnect(deviceId: String) async throws -> CommandResponse {
        let data = try await post(path: "/devices/\(deviceId)/disconnect")
        return try JSONDecoder().decode(CommandResponse.self, from: data)
    }

    // MARK: - Remote

    func sendCommand(_ command: String, action: String? = nil) async throws {
        var body: [String: String] = [:]
        if let action = action {
            body["action"] = action
        }
        _ = try await post(path: "/remote/\(command)", body: body.isEmpty ? nil : body)
    }

    // MARK: - Keyboard

    func sendText(_ text: String) async throws {
        let body = ["text": text]
        _ = try await post(path: "/keyboard", body: body)
    }

    func clearText() async throws {
        _ = try await post(path: "/keyboard/clear")
    }

    // MARK: - Status

    func getStatus() async throws -> StatusResponse {
        let data = try await get(path: "/status")
        return try JSONDecoder().decode(StatusResponse.self, from: data)
    }

    func healthCheck() async throws -> Bool {
        let data = try await get(path: "/health")
        let json = try JSONSerialization.jsonObject(with: data) as? [String: String]
        return json?["status"] == "ok"
    }

    // MARK: - HTTP

    private lazy var session: URLSession = {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 15
        return URLSession(configuration: config)
    }()

    private func makeURL(path: String) -> URL {
        URL(string: serverURL + path)!
    }

    private func get(path: String) async throws -> Data {
        let url = makeURL(path: path)
        let (data, response) = try await session.data(from: url)
        try validateResponse(response)
        return data
    }

    private func post(path: String, body: [String: String]? = nil) async throws -> Data {
        let url = makeURL(path: path)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let body = body {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        }

        let (data, response) = try await session.data(for: request)
        try validateResponse(response)
        return data
    }

    private func validateResponse(_ response: URLResponse) throws {
        guard let http = response as? HTTPURLResponse else { return }
        if http.statusCode >= 400 {
            throw APIError.serverError(statusCode: http.statusCode)
        }
    }
}

enum APIError: LocalizedError {
    case serverError(statusCode: Int)

    var errorDescription: String? {
        switch self {
        case .serverError(let code):
            return "서버 오류 (HTTP \(code))"
        }
    }
}
