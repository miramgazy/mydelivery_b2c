import api from './api'
import usersService from './users.service'

/**
 * Отчёт по заказам за период с бэкенда (один запрос, агрегация в БД).
 * Параметры: dateFrom, dateTo (YYYY-MM-DD).
 */
export async function fetchOrdersReportFromApi(dateFrom, dateTo) {
  const { data } = await api.get('/orders/report/', {
    params: { date_from: dateFrom, date_to: dateTo }
  })
  return {
    totalOrders: data.total_orders ?? 0,
    cancelledOrders: data.cancelled_orders ?? 0,
    totalSum: data.total_sum ?? 0,
    byTerminal: Array.isArray(data.by_terminal)
      ? data.by_terminal.map((x) => ({ name: x.name ?? '—', count: x.count ?? 0 }))
      : [],
    sumByTerminal: Array.isArray(data.sum_by_terminal)
      ? data.sum_by_terminal.map((x) => ({ name: x.name ?? '—', sum: x.sum ?? 0 }))
      : [],
    byPaymentType: Array.isArray(data.by_payment_type)
      ? data.by_payment_type.map((x) => ({ name: x.name ?? '—', count: x.count ?? 0 }))
      : [],
    sumByPaymentType: Array.isArray(data.sum_by_payment_type)
      ? data.sum_by_payment_type.map((x) => ({ name: x.name ?? '—', sum: x.sum ?? 0 }))
      : [],
    paidDeliveryCount: data.paid_delivery_count ?? 0,
    paidDeliverySum: data.paid_delivery_sum ?? 0,
    freeDeliveryCount: data.free_delivery_count ?? 0,
    freeDeliverySum: data.free_delivery_sum ?? 0,
    deliveryOrdersCount: data.delivery_orders_count ?? 0,
    deliveryOrdersSum: data.delivery_orders_sum ?? 0,
    pickupOrdersCount: data.pickup_orders_count ?? 0,
    pickupOrdersSum: data.pickup_orders_sum ?? 0
  }
}

/**
 * Заказы за период: запрос к API (fallback, если бэкенд не отдаёт /orders/report/).
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
  const isTmp = (o) => {
    if (!o || !o.order_number) return false
    const num = String(o.order_number).toUpperCase()
    return num.includes('TMP')
  }
  const validOrders = orders.filter((o) => !isTmp(o))
  const notCancelled = validOrders.filter((o) => !isCancelled(o))

  const byTerminal = {}
  const sumByTerminal = {}
  const byPaymentType = {}
  const sumByPaymentType = {}
  let paidDeliveryCount = 0
  let paidDeliverySum = 0
  let freeDeliveryCount = 0
  let freeDeliverySum = 0
  let deliveryOrdersCount = 0
  let deliveryOrdersSum = 0
  let pickupOrdersCount = 0
  let pickupOrdersSum = 0

  const isDelivery = (o) => {
    return !!(o.delivery_address_full || o.delivery_address || o.latitude || o.longitude)
  }

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

    const totalForType = total
    if (isDelivery(o)) {
      deliveryOrdersCount += 1
      deliveryOrdersSum += totalForType
    } else {
      pickupOrdersCount += 1
      pickupOrdersSum += totalForType
    }
  }

  const totalSum = notCancelled.reduce(
    (acc, o) => acc + Number(o.total_price ?? o.total_amount ?? 0) + Number(o.delivery_cost ?? 0),
    0
  )
  const cancelledCount = validOrders.filter(isCancelled).length

  return {
    totalOrders: notCancelled.length,
    cancelledOrders: cancelledCount,
    byTerminal: Object.entries(byTerminal).map(([name, count]) => ({ name, count })),
    sumByTerminal: Object.entries(sumByTerminal).map(([name, sum]) => ({ name, sum })),
    totalSum,
    byPaymentType: Object.entries(byPaymentType).map(([name, count]) => ({ name, count })),
    sumByPaymentType: Object.entries(sumByPaymentType).map(([name, sum]) => ({ name, sum })),
    paidDeliveryCount,
    paidDeliverySum,
    freeDeliveryCount,
    freeDeliverySum,
    deliveryOrdersCount,
    deliveryOrdersSum,
    pickupOrdersCount,
    pickupOrdersSum
  }
}

/**
 * Загрузка статистики по пользователям с бэкенда (один лёгкий запрос).
 * Учитывает всех пользователей, доступных текущему админу (в т.ч. 600+).
 */
export async function fetchUsersReportStatistics() {
  const { data } = await api.get('/users/statistics/')
  return {
    totalUsers: data.total_users ?? 0,
    subscribedCount: data.subscribed_count ?? 0,
    withVerifiedAddressCount: data.with_verified_address_count ?? 0,
    withPhoneCount: data.with_phone_count ?? 0,
    usersWithOrdersCount: data.users_with_orders_count ?? 0,
    byTerminal: Array.isArray(data.by_terminal)
      ? data.by_terminal.map((x) => ({ name: x.name ?? '—', count: x.count ?? 0 }))
      : []
  }
}

/**
 * Загрузка всех пользователей для отчёта (постранично).
 * Используется только как fallback, если бэкенд не отдаёт /users/statistics/.
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
