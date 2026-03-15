import api from './api'
import usersService from './users.service'

/**
 * Заказы за период: запрос к API с опциональными date_from, date_to.
 * Если бэкенд не фильтрует по дате — фильтрация по created_at на клиенте.
 */
export async function fetchOrdersForReport(dateFrom, dateTo) {
  const params = {}
  if (dateFrom) params.date_from = dateFrom
  if (dateTo) params.date_to = dateTo
  params.page_size = 5000
  const response = await api.get('/orders/', { params })
  const list = response.data?.results ?? response.data ?? []
  const fromTs = dateFrom ? new Date(dateFrom).setHours(0, 0, 0, 0) : null
  const toTs = dateTo ? new Date(dateTo).setHours(23, 59, 59, 999) : null
  const filtered = list.filter((o) => {
    const t = new Date(o.created_at).getTime()
    if (fromTs != null && t < fromTs) return false
    if (toTs != null && t > toTs) return false
    return true
  })
  return filtered
}

/**
 * Агрегация отчёта по заказам: количество, отменённые, по терминалам, суммы, по типам оплаты, платная/бесплатная доставка.
 */
export function aggregateOrdersReport(orders) {
  const cancelledStatuses = ['cancelled', 'Cancelled']
  const isCancelled = (o) => cancelledStatuses.includes(o.status)
  const notCancelled = orders.filter((o) => !isCancelled(o))

  const byTerminal = {}
  const sumByTerminal = {}
  const byPaymentType = {}
  const sumByPaymentType = {}
  let paidDeliveryCount = 0
  let paidDeliverySum = 0
  let freeDeliveryCount = 0
  let freeDeliverySum = 0

  for (const o of notCancelled) {
    const terminalName = o.terminal_name || '—'
    byTerminal[terminalName] = (byTerminal[terminalName] || 0) + 1
    const total = Number(o.total_price ?? o.total_amount ?? 0) + Number(o.delivery_cost ?? 0)
    sumByTerminal[terminalName] = (sumByTerminal[terminalName] || 0) + total

    const paymentName = o.payment_type_name || '—'
    byPaymentType[paymentName] = (byPaymentType[paymentName] || 0) + 1
    sumByPaymentType[paymentName] = (sumByPaymentType[paymentName] || 0) + total

    const deliveryCost = Number(o.delivery_cost ?? 0)
    if (deliveryCost > 0) {
      paidDeliveryCount += 1
      paidDeliverySum += deliveryCost
    } else {
      freeDeliveryCount += 1
    }
  }

  const totalSum = notCancelled.reduce(
    (acc, o) => acc + Number(o.total_price ?? o.total_amount ?? 0) + Number(o.delivery_cost ?? 0),
    0
  )
  const cancelledCount = orders.filter(isCancelled).length

  return {
    totalOrders: orders.length,
    cancelledOrders: cancelledCount,
    byTerminal: Object.entries(byTerminal).map(([name, count]) => ({ name, count })),
    sumByTerminal: Object.entries(sumByTerminal).map(([name, sum]) => ({ name, sum })),
    totalSum,
    byPaymentType: Object.entries(byPaymentType).map(([name, count]) => ({ name, count })),
    sumByPaymentType: Object.entries(sumByPaymentType).map(([name, sum]) => ({ name, sum })),
    paidDeliveryCount,
    paidDeliverySum,
    freeDeliveryCount,
    freeDeliverySum
  }
}

/**
 * Загрузка всех пользователей для отчёта (постранично).
 */
export async function fetchAllUsersForReport() {
  const pageSize = 500
  let page = 1
  let all = []
  let hasMore = true
  while (hasMore) {
    const data = await usersService.getUsers({ page, page_size: pageSize })
    const list = Array.isArray(data) ? data : (data?.results ?? [])
    const count = data?.count ?? list.length
    all = all.concat(list)
    hasMore = list.length === pageSize && all.length < count
    page += 1
  }
  return all
}

/**
 * Агрегация отчёта по пользователям: всего, подписанные, с подтверждённым адресом, по терминалам, с телефоном.
 */
export function aggregateUsersReport(users) {
  const subscribed = users.filter((u) => u.is_bot_subscribed === true)
  const withVerifiedAddress = users.filter((u) => {
    const addrs = u.addresses ?? []
    return addrs.some((a) => a?.is_verified)
  })
  const withPhone = users.filter((u) => u.phone && String(u.phone).trim().length > 0)

  const byTerminal = {}
  for (const u of users) {
    const terms = u.terminals ?? []
    if (terms.length === 0) {
      const key = 'Без терминала'
      byTerminal[key] = (byTerminal[key] || 0) + 1
    } else {
      for (const t of terms) {
        const name = typeof t === 'object' ? (t.name || t.terminal_group_name || t.id) : t
        const key = name ?? '—'
        byTerminal[key] = (byTerminal[key] || 0) + 1
      }
    }
  }

  return {
    totalUsers: users.length,
    subscribedCount: subscribed.length,
    withVerifiedAddressCount: withVerifiedAddress.length,
    withPhoneCount: withPhone.length,
    byTerminal: Object.entries(byTerminal).map(([name, count]) => ({ name, count }))
  }
}
