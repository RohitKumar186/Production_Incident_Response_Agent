
import apiClient from './client'

export interface VerificationResponse {
  incidentId?: string
  incident_id?: string
  status?: string

  recoveryStatus?: string
  recovery_status?: string

  checks?: unknown[] | Record<string, unknown>
  summary?: string
  verifiedAt?: string
  verified_at?: string

  result?: string
  next_step?: string
  recommended_next_step?: string

  service_recovered?: boolean
  recovery_metrics?: unknown
  verification_status?: string
  verification_details?: unknown

  schema_version?: string
  correlation_id?: string
  timestamp?: string
  producer?: string
  consumer?: string

  message?: string
  [key: string]: unknown
}

export async function getVerification(
  incidentId: string,
): Promise<VerificationResponse> {
  const response = await apiClient.get<
    VerificationResponse[] | VerificationResponse
  >(
    `/api/verifications/${encodeURIComponent(incidentId)}`,
  )

  const body: any = response.data

  // The API may return either an array or a single object.
  const result = Array.isArray(body)
    ? body[0]
    : body

  if (!result || typeof result !== 'object') {
    throw new Error(
      `No verification result found for ${incidentId}`,
    )
  }

  // The backend stores recovery checks inside verification_details.payload.
  const details =
    result.verification_details ??
    result.details ??
    {}

  const detailsObject: Record<string, any> =
    details && typeof details === 'object'
      ? details as Record<string, any>
      : {}

  const detailsPayload =
    detailsObject.payload ?? {}

  const embeddedVerification =
    detailsPayload.verification ??
    detailsObject.verification ??
    {}

  // Prefer the actual checks returned by the backend.
  const metrics =
    result.recovery_metrics ??
    embeddedVerification.checks ??
    detailsPayload.checks ??
    detailsObject.recovery_metrics ??
    detailsObject.metrics ??
    detailsObject.checks ??
    result.checks ??
    {}

  const recovered =
    result.service_recovered ??
    embeddedVerification.service_recovered ??
    detailsObject.service_recovered ??
    detailsObject.serviceRecovered

  const status =
    result.verification_status ??
    result.status ??
    embeddedVerification.status ??
    'UNKNOWN'

  const recoveryStatus =
    result.recoveryStatus ??
    result.recovery_status ??
    (recovered === true
      ? 'Recovered'
      : recovered === false
        ? 'Not recovered'
        : undefined)

  const verificationMessage =
    result.result ??
    embeddedVerification.message ??
    result.message ??
    detailsObject.message ??
    detailsObject.summary ??
    (recovered === true
      ? 'Service recovery verified successfully.'
      : recovered === false
        ? 'Service recovery was not confirmed.'
        : undefined)

  const nextStep =
    result.recommended_next_step ??
    result.next_step ??
    embeddedVerification.recommended_next_step ??
    detailsObject.recommended_next_step

  return {
    ...result,

    incidentId:
      result.incidentId ??
      result.incident_id ??
      incidentId,

    incident_id:
      result.incident_id ??
      result.incidentId ??
      incidentId,

    status,
    verification_status: status,

    recoveryStatus,
    recovery_status:
      result.recovery_status ??
      recoveryStatus,

    service_recovered: recovered,

    recovery_metrics: metrics,

    checks:
      result.checks ??
      embeddedVerification.checks ??
      detailsObject.checks ??
      metrics,

    result: verificationMessage,

    message:
      result.message ??
      verificationMessage,

    next_step: nextStep,
    recommended_next_step: nextStep,

    verification_details: details,
  }
}
