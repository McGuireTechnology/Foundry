import SwiftUI

struct RootView: View {
    @EnvironmentObject private var session: AppSession

    var body: some View {
        ZStack {
            FoundryPalette.appBackground
                .ignoresSafeArea()

            if session.route == .dashboard {
                DashboardLayoutView()
            } else {
                AuthLayoutView()
            }
        }
    }
}

private struct AuthLayoutView: View {
    @EnvironmentObject private var session: AppSession

    var body: some View {
        VStack(spacing: 16) {
            if let authBanner = session.authBanner {
                BannerView(text: authBanner)
                    .frame(maxWidth: 520)
            }

            switch session.route {
            case .signIn:
                SignInView()
            case .signUp:
                SignUpView()
            case .forgotPassword:
                ForgotPasswordView()
            case .resetPassword:
                ResetPasswordView()
            case .signOut:
                SignOutView()
            case .dashboard:
                EmptyView()
            }
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

private struct DashboardLayoutView: View {
    @EnvironmentObject private var session: AppSession

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            HStack(alignment: .center, spacing: 16) {
                FoundryWordmark(isLarge: false)
                Spacer()

                HStack(spacing: 18) {
                    Button("Dashboard") {
                        session.showDashboard()
                    }
                    .buttonStyle(.plain)
                    .foregroundStyle(FoundryPalette.linkBlue)
                    .font(.system(size: 15, weight: .semibold))

                    Button("Sign Out") {
                        session.startSignOut()
                    }
                    .buttonStyle(.plain)
                    .foregroundStyle(FoundryPalette.linkBlue)
                    .font(.system(size: 15, weight: .medium))
                }
            }

            if let authBanner = session.authBanner {
                BannerView(text: authBanner)
            }

            DashboardView()
        }
        .padding(24)
        .frame(maxWidth: 960)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
    }
}

struct FoundryWordmark: View {
    let isLarge: Bool

    var body: some View {
        HStack(alignment: .center, spacing: isLarge ? 14 : 12) {
            FoundryLogoMark()
                .frame(width: isLarge ? 56 : 48, height: isLarge ? 56 : 48)

            VStack(alignment: .leading, spacing: isLarge ? 6 : 2) {
                Text("Foundry")
                    .font(.system(size: isLarge ? 36 : 32, weight: .bold))
                    .foregroundStyle(FoundryPalette.textPrimary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)

                Text("by McGuire Technology, LLC")
                    .font(.system(size: isLarge ? 17 : 13, weight: .medium))
                    .foregroundStyle(FoundryPalette.textSecondary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.85)
            }
        }
    }
}

private struct BannerView: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.system(size: 14, weight: .medium))
            .foregroundStyle(FoundryPalette.bannerText)
            .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .background(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(FoundryPalette.bannerBackground)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .stroke(FoundryPalette.bannerBorder, lineWidth: 1)
        )
    }
}

struct FoundryLogoMark: View {
    var body: some View {
        GeometryReader { geometry in
            let width = geometry.size.width
            let height = geometry.size.height

            ZStack {
                Polygon(points: [
                    CGPoint(x: 0.5, y: 0.0),
                    CGPoint(x: 1.0, y: 0.285),
                    CGPoint(x: 0.5, y: 0.535),
                    CGPoint(x: 0.0, y: 0.285)
                ])
                .fill(FoundryPalette.logoCyan)

                Polygon(points: [
                    CGPoint(x: 1.0, y: 0.285),
                    CGPoint(x: 1.0, y: 0.87),
                    CGPoint(x: 0.5, y: 1.0),
                    CGPoint(x: 0.5, y: 0.535)
                ])
                .fill(FoundryPalette.logoMagenta)

                Polygon(points: [
                    CGPoint(x: 0.0, y: 0.285),
                    CGPoint(x: 0.0, y: 0.87),
                    CGPoint(x: 0.5, y: 1.0),
                    CGPoint(x: 0.5, y: 0.535)
                ])
                .fill(FoundryPalette.logoYellow)

                Path { path in
                    path.move(to: CGPoint(x: width * 0.5, y: height * 0.535))
                    path.addLine(to: CGPoint(x: width * 0.5, y: height))
                }
                .stroke(FoundryPalette.logoCenterLine, style: StrokeStyle(lineWidth: 2.2, lineCap: .round))
            }
        }
        .aspectRatio(1, contentMode: .fit)
    }
}

private struct Polygon: Shape {
    let points: [CGPoint]

    func path(in rect: CGRect) -> Path {
        var path = Path()
        guard let firstPoint = points.first else {
            return path
        }

        path.move(to: CGPoint(x: rect.minX + firstPoint.x * rect.width, y: rect.minY + firstPoint.y * rect.height))
        for point in points.dropFirst() {
            path.addLine(to: CGPoint(x: rect.minX + point.x * rect.width, y: rect.minY + point.y * rect.height))
        }
        path.closeSubpath()
        return path
    }
}

struct FoundryPanelStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(FoundryPalette.panelBackground)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(FoundryPalette.panelBorder, lineWidth: 1)
            )
    }
}

extension View {
    func foundryPanelStyle() -> some View {
        modifier(FoundryPanelStyle())
    }
}

enum FoundryPalette {
    static let appBackground = Color.black
    static let panelBackground = Color.black
    static let panelBorder = Color(red: 0.165, green: 0.184, blue: 0.267)

    static let textPrimary = Color(red: 0.962, green: 0.969, blue: 1.0)
    static let textSecondary = Color(red: 0.722, green: 0.749, blue: 0.831)
    static let textError = Color(red: 1.0, green: 0.541, blue: 0.478)
    static let textSuccess = Color(red: 0.45, green: 0.851, blue: 0.624)

    static let inputBackground = Color(red: 0.055, green: 0.075, blue: 0.141)
    static let inputBorder = Color(red: 0.164, green: 0.204, blue: 0.314)
    static let buttonBackground = Color(red: 0.227, green: 0.424, blue: 0.878)
    static let linkBlue = Color(red: 0.592, green: 0.714, blue: 1.0)
    static let linkPurple = Color(red: 0.819, green: 0.667, blue: 1.0)

    static let bannerBackground = Color(red: 0.059, green: 0.11, blue: 0.224)
    static let bannerBorder = Color(red: 0.173, green: 0.275, blue: 0.49)
    static let bannerText = Color(red: 0.812, green: 0.878, blue: 1.0)

    static let logoCyan = Color(red: 0.0, green: 0.682, blue: 0.937)
    static let logoMagenta = Color(red: 0.925, green: 0.0, blue: 0.549)
    static let logoYellow = Color(red: 1.0, green: 0.949, blue: 0.0)
    static let logoCenterLine = Color.black.opacity(0.22)
}
