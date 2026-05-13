import Foundation

struct VortexAPIClient {
    private let environment: AppEnvironment
    private let urlSession: URLSession
    private let jsonDecoder = JSONDecoder()
    private let jsonEncoder = JSONEncoder()

    init(environment: AppEnvironment, urlSession: URLSession = .shared) {
        self.environment = environment
        self.urlSession = urlSession
    }

    func health() async throws -> HealthResponse {
        try await send(path: "/health", method: "GET", body: Optional<Data>.none, accessToken: nil)
    }

    func login(email: String, password: String) async throws -> TokenPair {
        let payload = TokenRequestPayload(email: email, password: password)
        let body = try jsonEncoder.encode(payload)
        return try await send(path: "/auth/token", method: "POST", body: body, accessToken: nil)
    }

    func refresh(refreshToken: String) async throws -> TokenPair {
        let payload = RefreshTokenRequestPayload(refreshToken: refreshToken)
        let body = try jsonEncoder.encode(payload)
        return try await send(path: "/auth/refresh", method: "POST", body: body, accessToken: nil)
    }

    func users(accessToken: String) async throws -> [VortexUser] {
        try await send(path: "/users", method: "GET", body: Optional<Data>.none, accessToken: accessToken)
    }

    func createUser(email: String, password: String) async throws -> VortexUser {
        let payload = TokenRequestPayload(email: email, password: password)
        let body = try jsonEncoder.encode(payload)
        return try await send(path: "/users", method: "POST", body: body, accessToken: nil)
    }

    func forgotPassword(email: String) async throws -> ForgotPasswordResponse {
        let payload = ForgotPasswordRequestPayload(email: email)
        let body = try jsonEncoder.encode(payload)
        return try await send(path: "/auth/forgot-password", method: "POST", body: body, accessToken: nil)
    }

    func resetPassword(token: String, newPassword: String) async throws -> MessageResponse {
        let payload = ResetPasswordRequestPayload(token: token, newPassword: newPassword)
        let body = try jsonEncoder.encode(payload)
        return try await send(path: "/auth/reset-password", method: "POST", body: body, accessToken: nil)
    }

    private func send<Response: Decodable>(
        path: String,
        method: String,
        body: Data?,
        accessToken: String?
    ) async throws -> Response {
        let request = try buildRequest(path: path, method: method, body: body, accessToken: accessToken)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await urlSession.data(for: request)
        } catch {
            throw VortexAPIError.transport(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw VortexAPIError.invalidResponse
        }

        guard (200 ... 299).contains(httpResponse.statusCode) else {
            let message = parseErrorMessage(from: data, statusCode: httpResponse.statusCode)
            throw VortexAPIError.server(statusCode: httpResponse.statusCode, message: message)
        }

        do {
            return try jsonDecoder.decode(Response.self, from: data)
        } catch {
            throw VortexAPIError.decoding(error)
        }
    }

    private func buildRequest(
        path: String,
        method: String,
        body: Data?,
        accessToken: String?
    ) throws -> URLRequest {
        let normalizedPath = path.hasPrefix("/") ? path : "/\(path)"
        guard let url = URL(string: normalizedPath, relativeTo: environment.baseURL)?.absoluteURL else {
            throw VortexAPIError.invalidURL(path)
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.timeoutInterval = 15
        request.setValue(environment.apiVersion, forHTTPHeaderField: "X-API-Version")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        if let accessToken {
            request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = body
        }

        return request
    }

    private func parseErrorMessage(from data: Data, statusCode: Int) -> String {
        if let envelope = try? jsonDecoder.decode(APIErrorEnvelope.self, from: data) {
            return envelope.detail
        }

        return HTTPURLResponse.localizedString(forStatusCode: statusCode)
    }
}

enum VortexAPIError: Error, LocalizedError {
    case invalidURL(String)
    case invalidResponse
    case transport(Error)
    case decoding(Error)
    case server(statusCode: Int, message: String)

    var isUnauthorized: Bool {
        if case let .server(statusCode, _) = self {
            return statusCode == 401
        }
        return false
    }

    var errorDescription: String? {
        switch self {
        case let .invalidURL(path):
            return "Invalid API URL path: \(path)."
        case .invalidResponse:
            return "The API returned an unexpected response."
        case let .transport(error):
            return "Network error: \(error.localizedDescription)"
        case let .decoding(error):
            return "Unable to parse API response: \(error.localizedDescription)"
        case let .server(statusCode, message):
            return "API error (\(statusCode)): \(message)"
        }
    }
}

private struct TokenRequestPayload: Encodable {
    let email: String
    let password: String
}

private struct RefreshTokenRequestPayload: Encodable {
    let refreshToken: String

    enum CodingKeys: String, CodingKey {
        case refreshToken = "refresh_token"
    }
}

private struct ForgotPasswordRequestPayload: Encodable {
    let email: String
}

private struct ResetPasswordRequestPayload: Encodable {
    let token: String
    let newPassword: String

    enum CodingKeys: String, CodingKey {
        case token
        case newPassword = "new_password"
    }
}
