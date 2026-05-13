import Foundation

struct ForgotPasswordSubmissionResult {
    let errorMessage: String?
    let successMessage: String?
    let resetToken: String?
}

@MainActor
final class AppSession: ObservableObject {
    enum AuthStatus {
        case signedOut
        case signingIn
        case signedIn
    }

    enum Route {
        case dashboard
        case signIn
        case signUp
        case forgotPassword
        case resetPassword
        case signOut
    }

    @Published private(set) var authStatus: AuthStatus = .signedOut
    @Published private(set) var route: Route = .signIn
    @Published private(set) var authBanner: String?
    @Published private(set) var signedInEmail = ""
    @Published private(set) var prefilledEmail = ""
    @Published private(set) var prefilledResetToken = ""
    @Published private(set) var signedOut = false
    @Published private(set) var hasRememberedEmail = false

    private let client: VortexAPIClient
    private let credentialsStore: CredentialsStore

    private var accessToken: String?
    private var refreshToken: String?
    private var didBootstrap = false

    init(
        environment: AppEnvironment = .current,
        credentialsStore: CredentialsStore = .shared
    ) {
        self.client = VortexAPIClient(environment: environment)
        self.credentialsStore = credentialsStore
    }

    var isAuthenticated: Bool {
        authStatus == .signedIn
    }

    var isSigningIn: Bool {
        authStatus == .signingIn
    }

    func bootstrap() async {
        guard !didBootstrap else {
            return
        }
        didBootstrap = true

        if let tokens = credentialsStore.loadTokens() {
            accessToken = tokens.accessToken
            refreshToken = tokens.refreshToken
            signedInEmail = credentialsStore.loadCurrentUserEmail()
            hasRememberedEmail = !credentialsStore.loadRememberedEmail().isEmpty
            authStatus = .signedIn
            route = .dashboard
            signedOut = false
        } else {
            authStatus = .signedOut
            prefilledEmail = credentialsStore.loadRememberedEmail()
            hasRememberedEmail = !prefilledEmail.isEmpty
            route = .signIn
        }
    }

    func showDashboard() {
        guard isAuthenticated else {
            showSignIn()
            return
        }
        route = .dashboard
    }

    func showSignIn() {
        route = .signIn
        if prefilledEmail.isEmpty {
            prefilledEmail = credentialsStore.loadRememberedEmail()
        }
        hasRememberedEmail = !credentialsStore.loadRememberedEmail().isEmpty
    }

    func showSignUp() {
        route = .signUp
    }

    func showForgotPassword() {
        route = .forgotPassword
    }

    func showResetPassword(prefilledToken: String = "") {
        if !prefilledToken.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            prefilledResetToken = prefilledToken.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        route = .resetPassword
    }

    func startSignOut() {
        clearSession()
        route = .signOut
        signedOut = true
    }

    func clearBanner() {
        authBanner = nil
    }

    func signIn(email: String, password: String, rememberMe: Bool) async -> String? {
        if isSigningIn {
            return nil
        }

        let normalizedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalizedEmail.isEmpty, !password.isEmpty else {
            return "Enter an email and password to continue."
        }

        authStatus = .signingIn
        defer {
            if authStatus == .signingIn {
                authStatus = .signedOut
            }
        }

        do {
            let tokens = try await client.login(email: normalizedEmail, password: password)
            storeSession(tokens: tokens, email: normalizedEmail)
            if rememberMe {
                credentialsStore.rememberEmail(normalizedEmail)
            } else {
                credentialsStore.clearRememberedEmail()
            }
            hasRememberedEmail = rememberMe
            prefilledEmail = normalizedEmail
            authStatus = .signedIn
            signedOut = false
            authBanner = nil
            route = .dashboard
            return nil
        } catch {
            return mapSignInError(error)
        }
    }

    func signUp(email: String, password: String) async -> String? {
        let normalizedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalizedEmail.isEmpty, !password.isEmpty else {
            return "Please provide an email and password."
        }

        do {
            _ = try await client.createUser(email: normalizedEmail, password: password)
            prefilledEmail = normalizedEmail
            authBanner = "Account created. You can now sign in."
            route = .signIn
            return nil
        } catch let apiError as VortexAPIError {
            if case .server(409, _) = apiError {
                return "An account with this email already exists. Please sign in instead, or use a different email."
            }
            if apiError.isTimedOut {
                return "Request timed out. Please make sure the API is running and try again."
            }
            if apiError.isConnectivityError {
                return "Unable to reach the API. Please try again."
            }
            return "Sign up failed. Please review your input."
        } catch {
            return "Unable to reach the API. Please try again."
        }
    }

    func forgotPassword(email: String) async -> ForgotPasswordSubmissionResult {
        let normalizedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalizedEmail.isEmpty else {
            return ForgotPasswordSubmissionResult(
                errorMessage: "Please provide your account email.",
                successMessage: nil,
                resetToken: nil
            )
        }

        do {
            let response = try await client.forgotPassword(email: normalizedEmail)
            return ForgotPasswordSubmissionResult(
                errorMessage: nil,
                successMessage: response.message,
                resetToken: response.resetToken
            )
        } catch let apiError as VortexAPIError {
            if apiError.isTimedOut {
                return ForgotPasswordSubmissionResult(
                    errorMessage: "Request timed out. Please make sure the API is running and try again.",
                    successMessage: nil,
                    resetToken: nil
                )
            }
            if apiError.isConnectivityError {
                return ForgotPasswordSubmissionResult(
                    errorMessage: "Unable to reach the API. Please try again.",
                    successMessage: nil,
                    resetToken: nil
                )
            }
            return ForgotPasswordSubmissionResult(
                errorMessage: "Unable to process your request right now. Please try again.",
                successMessage: nil,
                resetToken: nil
            )
        } catch {
            return ForgotPasswordSubmissionResult(
                errorMessage: "Unable to reach the API. Please try again.",
                successMessage: nil,
                resetToken: nil
            )
        }
    }

    func resetPassword(token: String, newPassword: String) async -> String? {
        let trimmedToken = token.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedToken.isEmpty, !newPassword.isEmpty else {
            return "Enter a reset token and a new password."
        }

        do {
            _ = try await client.resetPassword(token: trimmedToken, newPassword: newPassword)
            authBanner = "Password reset complete. You can now sign in."
            route = .signIn
            prefilledResetToken = ""
            return nil
        } catch let apiError as VortexAPIError {
            if apiError.isTimedOut {
                return "Request timed out. Please make sure the API is running and try again."
            }
            if apiError.isConnectivityError {
                return "Unable to reach the API. Please try again."
            }
            return "Unable to reset password. Verify your token and try again."
        } catch {
            return "Unable to reach the API. Please try again."
        }
    }

    private func storeSession(tokens: TokenPair, email: String) {
        accessToken = tokens.accessToken
        refreshToken = tokens.refreshToken
        signedInEmail = email
        credentialsStore.saveSession(tokens: tokens, currentUserEmail: email)
    }

    private func clearSession() {
        accessToken = nil
        refreshToken = nil
        signedInEmail = ""
        authStatus = .signedOut
        credentialsStore.clearSession()
    }

    private func mapSignInError(_ error: Error) -> String {
        guard let apiError = error as? VortexAPIError else {
            return "Unable to reach the API. Please try again."
        }

        if case let .server(statusCode, detail) = apiError, statusCode == 429 {
            return detail
        }
        if apiError.isTimedOut {
            return "Request timed out. Please make sure the API is running and try again."
        }
        if apiError.isConnectivityError {
            return "Unable to reach the API. Please try again."
        }
        return "Sign in failed. Check your email and password."
    }
}

private extension VortexAPIError {
    var isTimedOut: Bool {
        guard case let .transport(error) = self else {
            return false
        }
        return (error as? URLError)?.code == .timedOut
    }

    var isConnectivityError: Bool {
        switch self {
        case .transport:
            return true
        default:
            return false
        }
    }
}
