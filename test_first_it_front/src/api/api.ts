import axios from 'axios'


export type defaultGuideItem = {
    id: string,
    name: string
}

export type guideWithRelationsItem = {
    id: string,
    name: string,
    category: defaultGuideItem
}

export interface GuideItem {
    id: string
    name: string
}

export interface RelationGuideItem {
    id: string
    name: string
    category: GuideItem
}

export type CashFlowItem = {
    id: string,
    amount: number,
    comment: string,
    category: guideWithRelationsItem,
    type: {
        id: string,
        name: string
    },
    status: {
        id: string,
        name: string
    },
    created_at: Date,

}

export type CashFlowItemPayload = {
    amount: number,
    comment?: string,
    category: guideWithRelationsItem,
    type: string,
    status: string,
    created_at?: Date
}

export const apiInstance = axios.create({
    baseURL: __API_URL__,
    timeout: 3000
})