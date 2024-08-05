<i18n src="@/locales/topic-types.yaml"></i18n>

<i18n>
en:
  rows:
    name: Name
    score: Score
    title: Title
  cover: Cover
  hit_score: Score
  interest: Interest
  topic_size: Number of works
  works: Works
  interest_in_time: Interest in time
  related_record: Related records
  important_works: Most demanded works

cs:
  rows:
    name: Jméno
    score: Zájem
    title: Název
  interest: Zájem
  hit_score: Skóre
  topic_size: Počet děl
  works: Díla
  interest_in_time: Zájem v čase
  related_record: Související záznamy
  important_works: Nejpoptávanější díla
</i18n>

<template>
  <v-container fluid>
    <v-row v-if="record">
      <v-col>
        <h1 class="display-1">
          {{ record.name }}
          <v-chip
            label
            outlined
            color="orange"
            v-text="topicTypeHuman"
          ></v-chip>
          <v-chip
            v-if="topicType == 'psh'"
            label
            outlined
            class="ml-3"
            color="green"
          >
            {{ record.root_node }}
          </v-chip>
        </h1>
      </v-col>
    </v-row>

    <v-row v-if="!isEmpty(scoreData)">
      <v-col>
        <h2>{{ $t("interest") }}</h2>
      </v-col>
    </v-row>

    <v-row v-if="!isEmpty(scoreData)">
      <v-col>
        <table class="listing">
          <tr>
            <th>{{ $t("topic_size") }}</th>
            <td>{{ scoreData.topic_size }}</td>
          </tr>
          <tr>
            <th>{{ $t("hit_score") }}</th>
            <td>{{ scoreData.work_score }}</td>
          </tr>
        </table>
      </v-col>
    </v-row>

    <v-row v-if="!isEmpty(workData)">
      <v-col>
        <h2>{{ $t("works") }}</h2>
      </v-col>
    </v-row>

    <v-row v-if="!isEmpty(workData)">
      <v-col>
        <v-data-table
          :items="workData"
          :headers="[
            { text: $t('rows.title'), value: 'work.name' },
            { text: $t('rows.score'), value: 'hit_score', align: 'right' },
          ]"
          sort-by="hit_score"
          sort-desc
        >
          <template v-slot:item.work.name="{ item }">
            <router-link
              :to="{ name: 'work detail', params: { workId: item.work.pk } }"
              >{{ item.work.name }}</router-link
            >
          </template>
          <template v-slot:item.work.hit_score="{ item }">
            {{ formatNumber(props.item.hit_score) }}
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <h2 v-text="$t('interest_in_time')"></h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <ExplicitTopicHitChart :topic-type="topicType" :topic-id="topicId" />
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <h2 v-text="$t('important_works')"></h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-0">
        <ExplicitTopicImportantWorksWidget
          :topic-type="topicType"
          :topic-id="topicId"
        />
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <h2 v-text="$t('related_record')"></h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="py-0">
        <ExplicitTopicRelatedTopicsWidget
          :topic-type="topicType"
          :topic-id="topicId"
          standalone
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";
import isEmpty from "lodash/isEmpty";
import * as math from "mathjs";
import ExplicitTopicHitChart from "./ExplicitTopicHitChart";
import ExplicitTopicRelatedTopicsWidget from "./ExplicitTopicRelatedTopicsWidget";
import { mapActions, mapGetters } from "vuex";
import ExplicitTopicImportantWorksWidget from "./ExplicitTopicImportantWorksWidget";

export default {
  name: "ExplicitTopicDetail",
  components: {
    ExplicitTopicRelatedTopicsWidget,
    ExplicitTopicHitChart,
    ExplicitTopicImportantWorksWidget,
  },
  props: {
    topicId: { required: true, type: Number },
    topicType: { required: true, type: String },
  },
  data() {
    return {
      record: null,
      isLoading: false,
      scoreData: null,
      workData: [],
      numberFormat: {
        notation: "fixed",
        precision: 1,
      },
    };
  },
  computed: {
    ...mapGetters({
      selectedWorksetUUID: "selectedWorksetUUID",
    }),
    topicTypeHuman() {
      return this.$t("topic_type." + this.topicType);
    },
    detailUrl() {
      if (this.selectedWorksetUUID) {
        return `/api/bookrank/workset/${this.selectedWorksetUUID}/${this.topicType}/${this.topicId}/`;
      }
      return null;
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    async loadObject() {
      if (this.detailUrl) {
        this.isLoading = true;
        try {
          const response = await axios.get(this.detailUrl);
          this.record = response.data;
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching data: " + error,
            color: "error",
          });
          console.log("Error fetching data", error);
        } finally {
          this.isLoading = false;
        }
      }
    },
    isEmpty(obj) {
      return isEmpty(obj);
    },
    formatNumber(number) {
      return math.format(number, this.numberFormat);
    },
  },
  watch: {
    detailUrl() {
      this.loadObject();
    },
  },

  created() {
    this.loadObject();
  },
};
</script>

<style scoped lang="scss">
h2 {
  font-weight: 300;
}

div.fields {
  margin-top: 1rem;
}

div.overview {
  padding: 1rem 0 1rem 2.5rem;
}

table.listing {
  border-collapse: collapse;

  tr {
    th,
    td {
      border-bottom: solid 1px #dddddd;
    }

    &:last-of-type {
      th,
      td {
        border-bottom: none;
      }
    }
  }

  th {
    text-align: left;
    padding-right: 2.5rem;
  }
}

ul.simple {
  list-style: none;
  padding-left: 0;
}

img.book-cover {
  max-height: 240px;
}
</style>
