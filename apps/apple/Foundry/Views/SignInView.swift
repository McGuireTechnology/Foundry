import SwiftUI

struct SignInView: View {
    @EnvironmentObject private var session: AppSession

    @State private var email = ""
    @State private var password = ""
    @State private var rememberMe = false
    @State private var showPassword = false
    @State private var loading = false
    @State private var errorMessage = ""

    var body: some View {
        AuthPanel(title: "Sign In", subtitle: "Use your Foundry account credentials to continue.") {
            VStack(alignment: .leading, spacing: 14) {
                FoundryLabeledField(label: "Email") {
                    TextField("", text: $email)
                        .autocorrectionDisabled()
                        .foundryInputStyle()
                }

                FoundryLabeledField(label: "Password") {
                    Group {
                        if showPassword {
                            TextField("", text: $password)
                                .autocorrectionDisabled()
                        } else {
                            SecureField("", text: $password)
                        }
                    }
                    .foundryInputStyle()
                }

                CheckboxRow(title: "Show password", isOn: $showPassword)
                CheckboxRow(title: "Remember me", isOn: $rememberMe)

                Button {
                    submit()
                } label: {
                    Text(loading ? "Signing in..." : "Sign In")
                        .font(.system(size: 16, weight: .semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(FoundryPalette.buttonBackground)
                        .foregroundStyle(Color.white)
                        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                }
                .buttonStyle(.plain)
                .disabled(loading)
                .opacity(loading ? 0.8 : 1)

                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(FoundryPalette.textError)
                }
            }

            VStack(alignment: .leading, spacing: 10) {
                HStack(spacing: 6) {
                    Text("Need an account?")
                        .foregroundStyle(FoundryPalette.textPrimary)
                    Button("Create one") {
                        session.showSignUp()
                    }
                    .buttonStyle(.plain)
                    .foregroundStyle(FoundryPalette.linkPurple)
                    .underline()
                }

                HStack(spacing: 6) {
                    Text("Forgot your password?")
                        .foregroundStyle(FoundryPalette.textPrimary)
                    Button("Reset it") {
                        session.showForgotPassword()
                    }
                    .buttonStyle(.plain)
                    .foregroundStyle(FoundryPalette.linkBlue)
                    .underline()
                }
            }
            .font(.system(size: 16, weight: .medium))
        }
        .onAppear {
            if email.isEmpty {
                email = session.prefilledEmail
            }
            rememberMe = session.hasRememberedEmail
        }
    }

    private func submit() {
        guard !loading else {
            return
        }

        loading = true
        errorMessage = ""
        session.clearBanner()

        Task {
            let message = await session.signIn(email: email, password: password, rememberMe: rememberMe)
            if let message {
                errorMessage = message
            } else {
                password = ""
            }
            loading = false
        }
    }
}

struct SignUpView: View {
    @EnvironmentObject private var session: AppSession

    @State private var email = ""
    @State private var password = ""
    @State private var showPassword = false
    @State private var loading = false
    @State private var errorMessage = ""

    var body: some View {
        AuthPanel(title: "Sign Up", subtitle: "Create your Foundry account.") {
            VStack(alignment: .leading, spacing: 14) {
                FoundryLabeledField(label: "Email") {
                    TextField("", text: $email)
                        .autocorrectionDisabled()
                        .foundryInputStyle()
                }

                FoundryLabeledField(label: "Password") {
                    Group {
                        if showPassword {
                            TextField("", text: $password)
                                .autocorrectionDisabled()
                        } else {
                            SecureField("", text: $password)
                        }
                    }
                    .foundryInputStyle()
                }

                CheckboxRow(title: "Show password", isOn: $showPassword)

                Button {
                    submit()
                } label: {
                    Text(loading ? "Creating account..." : "Create Account")
                        .font(.system(size: 16, weight: .semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(FoundryPalette.buttonBackground)
                        .foregroundStyle(Color.white)
                        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                }
                .buttonStyle(.plain)
                .disabled(loading)
                .opacity(loading ? 0.8 : 1)

                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(FoundryPalette.textError)
                }
            }

            HStack(spacing: 6) {
                Text("Already registered?")
                    .foregroundStyle(FoundryPalette.textPrimary)
                Button("Sign in") {
                    session.showSignIn()
                }
                .buttonStyle(.plain)
                .foregroundStyle(FoundryPalette.linkBlue)
                .underline()
            }
            .font(.system(size: 16, weight: .medium))
        }
    }

    private func submit() {
        guard !loading else {
            return
        }

        loading = true
        errorMessage = ""
        session.clearBanner()

        Task {
            let message = await session.signUp(email: email, password: password)
            if let message {
                errorMessage = message
            }
            loading = false
        }
    }
}

struct ForgotPasswordView: View {
    @EnvironmentObject private var session: AppSession

    @State private var email = ""
    @State private var loading = false
    @State private var errorMessage = ""
    @State private var successMessage = ""
    @State private var resetToken: String?

    var body: some View {
        AuthPanel(
            title: "Forgot Password",
            subtitle: "Enter your email and we will send reset instructions if an account exists."
        ) {
            VStack(alignment: .leading, spacing: 14) {
                FoundryLabeledField(label: "Email") {
                    TextField("", text: $email)
                        .autocorrectionDisabled()
                        .foundryInputStyle()
                }

                Button {
                    submit()
                } label: {
                    Text(loading ? "Submitting..." : "Send Reset Instructions")
                        .font(.system(size: 16, weight: .semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(FoundryPalette.buttonBackground)
                        .foregroundStyle(Color.white)
                        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                }
                .buttonStyle(.plain)
                .disabled(loading)
                .opacity(loading ? 0.8 : 1)

                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(FoundryPalette.textError)
                }

                if !successMessage.isEmpty {
                    Text(successMessage)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(FoundryPalette.textSuccess)
                }

                if let resetToken, !resetToken.isEmpty {
                    HStack(spacing: 6) {
                        Text("Dev reset link:")
                            .foregroundStyle(FoundryPalette.textSuccess)
                        Button("Open Reset Password") {
                            session.showResetPassword(prefilledToken: resetToken)
                        }
                        .buttonStyle(.plain)
                        .foregroundStyle(FoundryPalette.linkBlue)
                        .underline()
                    }
                    .font(.system(size: 14, weight: .medium))
                }
            }

            HStack(spacing: 6) {
                Text("Remembered your password?")
                    .foregroundStyle(FoundryPalette.textPrimary)
                Button("Back to Sign In") {
                    session.showSignIn()
                }
                .buttonStyle(.plain)
                .foregroundStyle(FoundryPalette.linkBlue)
                .underline()
            }
            .font(.system(size: 16, weight: .medium))
        }
    }

    private func submit() {
        guard !loading else {
            return
        }

        loading = true
        errorMessage = ""
        successMessage = ""
        resetToken = nil
        session.clearBanner()

        Task {
            let result = await session.forgotPassword(email: email)
            errorMessage = result.errorMessage ?? ""
            successMessage = result.successMessage ?? ""
            resetToken = result.resetToken
            loading = false
        }
    }
}

struct ResetPasswordView: View {
    @EnvironmentObject private var session: AppSession

    @State private var token = ""
    @State private var newPassword = ""
    @State private var showPassword = false
    @State private var loading = false
    @State private var errorMessage = ""

    var body: some View {
        AuthPanel(title: "Reset Password", subtitle: "Enter your reset token and choose a new password.") {
            VStack(alignment: .leading, spacing: 14) {
                FoundryLabeledField(label: "Reset Token") {
                    TextField("", text: $token)
                        .autocorrectionDisabled()
                        .foundryInputStyle()
                }

                FoundryLabeledField(label: "New Password") {
                    Group {
                        if showPassword {
                            TextField("", text: $newPassword)
                                .autocorrectionDisabled()
                        } else {
                            SecureField("", text: $newPassword)
                        }
                    }
                    .foundryInputStyle()
                }

                CheckboxRow(title: "Show password", isOn: $showPassword)

                Button {
                    submit()
                } label: {
                    Text(loading ? "Resetting..." : "Reset Password")
                        .font(.system(size: 16, weight: .semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(FoundryPalette.buttonBackground)
                        .foregroundStyle(Color.white)
                        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                }
                .buttonStyle(.plain)
                .disabled(loading)
                .opacity(loading ? 0.8 : 1)

                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundStyle(FoundryPalette.textError)
                }
            }

            Button("Back to Sign In") {
                session.showSignIn()
            }
            .buttonStyle(.plain)
            .foregroundStyle(FoundryPalette.linkBlue)
            .underline()
            .font(.system(size: 16, weight: .medium))
        }
        .onAppear {
            if token.isEmpty {
                token = session.prefilledResetToken
            }
        }
    }

    private func submit() {
        guard !loading else {
            return
        }

        loading = true
        errorMessage = ""
        session.clearBanner()

        Task {
            let message = await session.resetPassword(token: token, newPassword: newPassword)
            if let message {
                errorMessage = message
            } else {
                newPassword = ""
            }
            loading = false
        }
    }
}

struct SignOutView: View {
    @EnvironmentObject private var session: AppSession

    var body: some View {
        AuthPanel(title: "Sign Out", subtitle: "") {
            if session.signedOut {
                Text("You have been signed out.")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(FoundryPalette.textSuccess)
            } else {
                Text("Signing you out...")
                    .font(.system(size: 16, weight: .medium))
                    .foregroundStyle(FoundryPalette.textPrimary)
            }

            Button("Go to Sign In") {
                session.showSignIn()
            }
            .buttonStyle(.plain)
            .foregroundStyle(FoundryPalette.linkBlue)
            .underline()
            .font(.system(size: 16, weight: .medium))
        }
    }
}

private struct AuthPanel<Content: View>: View {
    let title: String
    let subtitle: String
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            FoundryWordmark(isLarge: true)

            Text(title)
                .font(.system(size: 24, weight: .bold))
                .foregroundStyle(FoundryPalette.textPrimary)

            if !subtitle.isEmpty {
                Text(subtitle)
                    .font(.system(size: 16, weight: .regular))
                    .foregroundStyle(FoundryPalette.textPrimary)
                    .padding(.bottom, 2)
            }

            content
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 20)
        .frame(maxWidth: 520, alignment: .leading)
        .foundryPanelStyle()
    }
}

private struct FoundryLabeledField<Content: View>: View {
    let label: String
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(label)
                .font(.system(size: 15, weight: .regular))
                .foregroundStyle(FoundryPalette.textPrimary)
            content
        }
    }
}

private struct CheckboxRow: View {
    let title: String
    @Binding var isOn: Bool

    var body: some View {
        Button {
            isOn.toggle()
        } label: {
            HStack(spacing: 10) {
                Image(systemName: isOn ? "checkmark.square.fill" : "square")
                    .font(.system(size: 16))
                    .foregroundStyle(isOn ? FoundryPalette.linkBlue : FoundryPalette.textSecondary)
                Text(title)
                    .font(.system(size: 15, weight: .regular))
                    .foregroundStyle(FoundryPalette.textPrimary)
            }
        }
        .buttonStyle(.plain)
    }
}

private struct FoundryInputStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.system(size: 16, weight: .regular))
            .padding(.horizontal, 10)
            .padding(.vertical, 9)
            .background(
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .fill(FoundryPalette.inputBackground)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 6, style: .continuous)
                    .stroke(FoundryPalette.inputBorder, lineWidth: 1)
            )
            .foregroundStyle(FoundryPalette.textPrimary)
    }
}

private extension View {
    func foundryInputStyle() -> some View {
        modifier(FoundryInputStyle())
    }
}
